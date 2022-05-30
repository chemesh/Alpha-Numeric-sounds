import numpy as np
from utils.constants import WAV_FILE_TEST
from data.DataModels import Individual
from deap import base, creator, tools
import librosa

POPULATION_SIZE = 10


def main():
    creator.create("Fitness", base.Fitness, weights=(1.0,))
    creator.create("Individual", object, sr=int, raw_data=np.ndarray, fitness=creator.Fitness)
    toolbox = base.Toolbox()
    toolbox.register()


if __name__ == "__main__":
    main()
