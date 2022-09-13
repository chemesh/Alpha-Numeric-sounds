
class EA_Parameters:
    def __init__(self, generations, population, selection, mutation, crossover):
        self.max_gens = generations
        self.popsize = population
        self.selection_p = selection
        self.mutation_prob = mutation
        self.crossover_prob = crossover

    def json(self):
        return vars(self)