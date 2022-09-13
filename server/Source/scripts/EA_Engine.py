import math
import random
from copy import deepcopy

import deap.algorithms as dpa
import librosa.beat
from deap import base, creator, tools

import server.Source.utils.SoundUtils as su
from server.Source.utils.DataModels import SongPool, Song
from server.Source.utils.Logger import Logger
from server.Source.utils.Constants import POPULATION_SIZE, TOURNSIZE_PERCENT, CROSSOVER_PROBABILITY, MUTATION_PROBABILITY, SAMPLERATE
import server.Source.utils.Raters as raters
from server.Source.utils.SoundUtils import INSTRUMENT as inst


class EA_Engine(object):

    class _Fitness(object):
        method_list = None

        @classmethod
        def rate(cls, individual):
            if not cls.method_list:
                cls._init_method_list()
            return (sum([getattr(cls, method)(individual) for method in cls.method_list]) / len(cls.method_list),)

        @classmethod
        def _init_method_list(cls):
            cls.method_list = [func for func in dir(cls) if callable(getattr(cls, func)) and func.startswith("_sr")]

        @staticmethod
        def _sr1(individual: Song):
            bkps = individual.segments_frame_bkps
            bkps.insert(0, 0)
            sum_rates = num_rates = 0
            for bkp, next_bkp in zip(bkps[:-1], bkps[1:]):
                tempo, beat_track = librosa.beat.beat_track(individual.data[bkp:next_bkp], individual.sr)
                layers = su.separate_voices(individual.data[bkp:next_bkp])
                vocal_notes, _ = su.extract_notes(layers[inst.VOCALS.value], beat_track)
                rate_vocal_crazy = raters.sub_rater_neighboring_pitch(vocal_notes)
                piano_notes, _ = su.extract_notes(layers[inst.PIANO.value], beat_track)
                rate_piano_crazy = raters.sub_rater_neighboring_pitch(piano_notes)
                sum_rates += rate_piano_crazy + rate_vocal_crazy
                num_rates += 2
            return sum_rates / num_rates

        @staticmethod
        def _sr2(individual):
            bkps = individual.segments_frame_bkps
            bkps.insert(0, 0)
            # split each to layers
            sum_rates = num_rates = 0
            for bkp, next_bkp in zip(bkps[:-1], bkps[1:]):
                tempo, beat_track = librosa.beat.beat_track(individual.data[bkp:next_bkp], individual.sr)
                # rate piano and vocals (for each seg) with neigh_pitch
                layers = su.separate_voices(individual.data[bkp:next_bkp], sep="spleeter:2stems")
                vocal_notes, _ = su.extract_notes(layers[inst.VOCALS.value], beat_track)
                key = su.extract_key(layers[inst.VOCALS.value], individual.sr)
                sum_rates += raters.sub_rater_notes_in_key(vocal_notes, key)
                num_rates += 1
            # rate vocals by notes in key
            return sum_rates / num_rates

        @staticmethod
        def _sr4(individual):
            beat_track_frames = individual.beat_frames
            notes, _ = su.extract_notes(individual.data, beat_track_frames, individual.sr)
            return raters.sub_rater_quiet_notes(notes)

    def __init__(self, logger: Logger):
        self.toolbox = base.Toolbox()
        self.song_pool = SongPool()
        self.logger = logger

        creator.create("Fitness_test", base.Fitness, weights=(1.0,))
        # creator.create("Individual", object, sr=int, raw_data=np.ndarray, fitness=Fitness)
        creator.create("Individual", Song, fitness=creator.Fitness_test)
        # self.toolbox.register("individual_creator", self._individual_creator)
        # self.toolbox.register("population_creator", self._myInitRepeat, list, self.toolbox.individual_creator)
        self.toolbox.register("select", tools.selBest)
        self.toolbox.register("evaluate", self._Fitness.rate)
        self.toolbox.register("mutate", self._mutate)
        self.toolbox.register("mate", self._crossover)

    def get_audio_data(self):
        return self.song_pool.generate()

    def _population_creator(self, popsize):
        population = []
        for i in range(popsize):
            ind = self._individual_creator(i) if i == 0 or i == 1 else self._individual_creator()
            population.append(ind)
        return population

    def _individual_creator(self, idx=None):
        s = self.song_pool.generate() if idx is None else self.song_pool.get(idx)
        return creator.Individual(data=s, sr=SAMPLERATE)

    @classmethod
    def _mutate(cls, individual):
        inst = random.choice(su.INSTRUMENT.list() + [None])
        s, _ = su.rand_reconstruct(individual.data, individual.sr, individual.data, individual.sr, inst=inst)
        return creator.Individual(data=s, sr=SAMPLERATE),


    @classmethod
    def _crossover(cls, ind1, ind2):
        inst = random.choice(su.INSTRUMENT.list() + [None])
        s1, s2 = su.rand_reconstruct(ind1.data, ind1.sr, ind2.data, ind2.sr, inst=inst)
        return creator.Individual(data=s1, sr=SAMPLERATE), creator.Individual(data=s2, sr=SAMPLERATE)

    def _calculate_fitness_values(self, population):
        # calculate fitness tuple for each individual in the population:
        fitness_values = list(map(self.toolbox.evaluate, population))
        for individual, fitness_value in zip(population, fitness_values):
            individual.fitness.values = fitness_value

        # extract fitness values from all individuals in population:
        return [individual.fitness.values[0] for individual in population]

    def mix(
            self,
            *songs: Song,
            max_gens,
            popsize,
            selection_p,
            mutation_prob,
            crossover_prob):


        self.logger.info("adding songs to pool")
        su.adjust_bpm(songs[0], songs[1])
        su.adjust_pitch(songs[0], songs[1])
        self.song_pool.add(*songs)

        # create initial population (generation 0):
        self.logger.info("creating population")
        population = self._population_creator(popsize=popsize)

        # calculating the fitness value for each individual in the population
        _ = self._calculate_fitness_values(population)

        # initialize statistics accumulators:
        max_fitness_values = []
        mean_fitness_values = []

        for current_gen in range(1, max_gens + 1):

            self.logger.info(f"---------- Start running generation {current_gen} ----------")

            # apply the selection operator, to select the next generation's individuals:
            offspring = self.toolbox.select(population, math.ceil(selection_p * len(population)))
            self.logger.info(f"selected best {len(offspring)} individuals out of population of {len(population)}")

            # cloning the selected offsprings randomly until its size is popsize,
            # so no potential offsprings will be pruned in the next generation
            selected = offspring
            offspring = [deepcopy(random.choice(selected)) for _ in range(popsize - len(selected))] + selected

            self.logger.info("starting mating and mutating offsprings")
            population[:] = dpa.varAnd(
                population=offspring,
                toolbox=self.toolbox,
                cxpb=crossover_prob,
                mutpb=mutation_prob
            )
            self.logger.info(f"new population of {len(population)}")


            # collect fitnessValues into a list, update statistics and print:
            self.logger.info("calculating population fitness values")
            fitness_values = self._calculate_fitness_values(population)

            max_fitness = max(fitness_values)
            mean_fitness = sum(fitness_values) / len(population)
            max_fitness_values.append(max_fitness)
            mean_fitness_values.append(mean_fitness)
            self.logger.info(f"- Generation {current_gen}: Max Fitness = {max_fitness}, Avg Fitness = {mean_fitness}")

            # find and print best individual:
            best_index = fitness_values.index(max(fitness_values))
            self.logger.info(f"Best Individual = {population[best_index]}")


        # return the top best individuals created
        return sorted(population, key=lambda ind: max(ind.fitness.values), reverse=True)[:3]



