import copy
import numpy as np
from deap import base, creator, tools

from utils.DataModels import SongPool
from utils.constants import POPULATION_SIZE, TOURNSIZE_PERCENT, CROSSOVER_PROBABILITY, MUTATION_PROBABILITY


class EA_Engine(object):
    def __init__(self):
        self.toolbox = base.Toolbox()
        self.song_pool = SongPool()

        creator.create("Fitness_test", base.Fitness, weights=(1.0,))
        # creator.create("Individual", object, sr=int, raw_data=np.ndarray, fitness=Fitness)
        creator.create("Individual", object, sr=int, raw_data=np.ndarray, fitness=creator.Fitness_test)

    def _register(self, population_size, tournsize_percent):
        self.toolbox.register("get_audio_data", self.song_pool.pop())
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

    def mix(self,
            song1,
            song2,
            gens=10,
            bkps=0,
            popsize=POPULATION_SIZE,
            tournsize_p=TOURNSIZE_PERCENT,
            mutation_prob=MUTATION_PROBABILITY,
            crossover_prob=CROSSOVER_PROBABILITY):

        self._register(popsize, tournsize_p)
