import random

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
            max_bkps = su.get_max_bkps(individual.tempo, individual.duration)
            _, bkps = su.break_to_timed_segments(individual.data, max_bkps,
                                                 return_indi_segments=False, return_bkps_as_frames=True)
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
            # get timed segments
            max_bkps = su.get_max_bkps(individual.tempo, individual.duration)
            _, bkps = su.break_to_timed_segments(individual.data, max_bkps,
                                                 return_indi_segments=False, return_bkps_as_frames=True)
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

    def __init__(self, logger: Logger):
        self.toolbox = base.Toolbox()
        self.song_pool = SongPool()
        self.logger = logger

        creator.create("Fitness_test", base.Fitness, weights=(1.0,))
        # creator.create("Individual", object, sr=int, raw_data=np.ndarray, fitness=Fitness)
        creator.create("Individual", Song, fitness=creator.Fitness_test)
        self.toolbox.register("individual_creator", self._individual_creator)
        self.toolbox.register("population_creator", tools.initRepeat, list, self.toolbox.individual_creator)
        self.toolbox.register("select", tools.selBest)
        self.toolbox.register("evaluate", self._Fitness.rate)
        self.toolbox.register("mutate", self._mutate)
        self.toolbox.register("mate", self._crossover)

    def get_audio_data(self):
        return self.song_pool.generate()

    def _individual_creator(self):
        s = self.song_pool.generate()
        return creator.Individual(data=s, sr=SAMPLERATE)

    @classmethod
    def _mutate(cls, individual):
        # todo should we put here librosa.effects.remix() instead?
        return EA_Engine._crossover(individual, individual)

    @classmethod
    def _crossover(cls, ind1, ind2):
        inst = random.choice(su.INSTRUMENT.list() + [None])
        s = su.rand_reconstruct(ind1.data, ind1.sr, ind2.data, ind2.sr, inst=inst)
        return creator.Individual(data=s, sr=SAMPLERATE)

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
            max_gens=10,
            num_of_bkps=0,
            popsize=POPULATION_SIZE,
            tournsize_p=TOURNSIZE_PERCENT,
            mutation_prob=MUTATION_PROBABILITY,
            crossover_prob=CROSSOVER_PROBABILITY):

        su.adjust_bpm(songs[0], songs[1])
        su.adjust_pitch(songs[0], songs[1])

        self.song_pool.add(*songs)
        # create initial population (generation 0):
        population = self.toolbox.population_creator(n=popsize)
        gen_counter = 0

        bkps = self._get_bkps(num_of_bkps, max_gens)

        final_pop, logbook = dpa.eaMuPlusLambda(
            population=population,
            toolbox=self.toolbox,
            mu=popsize,
            lambda_=popsize,
            cxpb=crossover_prob,
            mutpb=mutation_prob,
            ngen=max_gens,
            verbose=True
        )

        # return the top best individuals created
        return sorted(final_pop, key=lambda ind: max(ind.fitness.values), reverse=True)[:3]



