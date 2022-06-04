import librosa
import librosa.display
import soundfile as sf
import matplotlib.pyplot as plt
import numpy as np

from utils.Logger import Logger
from utils.Constants import WAV_FILE_TEST, INPUT_FOLDER
from EA_Engine import EA_Engine
from utils.DataModels import Song


def main():
    logger = Logger()
    engine = EA_Engine(logger)

    song1 = Song(WAV_FILE_TEST)
    song2 = Song(librosa.ex('nutcracker'))

    results = engine.mix(song1, song2)
    for i in range(len(results)):
        sf.write(f"{INPUT_FOLDER}/result_{i}.wav", results[i].data, results[i].sr)


if __name__ == "__main__":
    main()
