import copy
import random

import numpy as np
from deap import base, creator, tools

from utils.DataModels import SongPool, Song
from utils.Logger import Logger
from utils.Constants import POPULATION_SIZE, TOURNSIZE_PERCENT, CROSSOVER_PROBABILITY, MUTATION_PROBABILITY
from utils.CommonUtils import is_converged


class EA_Engine(object):
    def __init__(self, logger: Logger):
        self.toolbox = base.Toolbox()
        self.song_pool = SongPool()
        self.logger = logger

        creator.create("Fitness_test", base.Fitness, weights=(1.0,))
        # creator.create("Individual", object, sr=int, raw_data=np.ndarray, fitness=Fitness)
        creator.create("Individual", object, sr=int, raw_data=np.ndarray, fitness=creator.Fitness_test)

    def _register(self, population_size, tournsize_percent):
        # todo: need to find alternative to register once and change popsiz and tournsize values if needed
        self.toolbox.register("get_audio_data", lambda: self.song_pool.pop())
        self.toolbox.register("individual_creator", tools.initRepeat, creator.Individual, self.toolbox.get_audio_data, n=1)
        self.toolbox.register("population_creator", tools.initRepeat, list, self.toolbox.individual_creator)
        self.toolbox.register("select", tools.selTournament, tournsize=population_size * tournsize_percent)
        self.toolbox.register("evaluate", self._Fitness.rate)
        self.toolbox.register("mutate", EA_Engine._mutate)
        self.toolbox.register("mate", EA_Engine._crossover)


    @staticmethod
    def _mutate(individual):
        return copy.deepcopy(individual)

    @staticmethod
    def _crossover(ind1, ind2):
        return ind1 + ind2

    class _Fitness(object):
        @classmethod
        def rate(cls, individual):
            # todo: consider calling methods in different threads for more efficiency
            # todo: find a way to create 'method_list' one time only at the initialization
            method_list = [func for func in dir() if callable(getattr(cls, func)) and func.startswith("_sr")]
            return sum([getattr(cls, method)(individual) for method in method_list]) / len(method_list)

        @staticmethod
        def _sr1(individual):
            return 1

        @staticmethod
        def _sr2(individual):
            return 1

    def _get_bkps(self, num_of_bkps, gens):
        if num_of_bkps > 0:
            bkps = set()
            coef = gens / num_of_bkps
            for i in range(num_of_bkps):
                bkps.add(i * coef)
            return bkps
        else:
            return None

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

        self._register(popsize, tournsize_p)
        self.song_pool.add(songs)

        # create initial population (generation 0):
        population = self.toolbox.population_creator(n=POPULATION_SIZE)
        gen_counter = 0

        # set which generations should  mark a break point in the mixing executions
        # todo: implement logic for returning on breakpoints
        bkps = self._get_bkps(num_of_bkps, max_gens)

        _ = self._calculate_fitness_values(population)

        # initialize statistics accumulators:
        max_fitness_values = []
        mean_fitness_values = []

        # main evolutionary loop
        while not is_converged(max_fitness_values) and gen_counter < max_gens:

            gen_counter += 1
            self.logger.info(f"---------- Start running generation {gen_counter} ----------")

            # apply the selection operator, to select the next generation's individuals:
            offspring = self.toolbox.select(population, len(population))
            # clone the selected individuals:
            offspring = list(map(self.toolbox.clone, offspring))

            # apply the crossover operator to pairs of offspring:
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random < crossover_prob:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < mutation_prob:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # replace the current population with the offspring:
            population[:] = offspring

            # collect fitnessValues into a list, update statistics and print:
            fitness_values = self._calculate_fitness_values(population)

            max_fitness = max(fitness_values)
            mean_fitness = sum(fitness_values) / len(population)
            max_fitness_values.append(max_fitness)
            mean_fitness_values.append(mean_fitness)
            self.logger.info(f"- Generation {gen_counter}: Max Fitness = {max_fitness}, Avg Fitness = {mean_fitness}")

            # find and print best individual:
            best_index = fitness_values.index(max(fitness_values))
            self.logger.info(f"Best Individual = {population[best_index]}")

        # return the top best individuals created
        return sorted(population, key=lambda ind: max(ind.fitness.values), reverse=True)[:3]

