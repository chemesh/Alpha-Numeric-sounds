import os
import sys

import librosa
import librosa.display
import soundfile as sf

from utils.Logger import Logger
from utils.Constants import WAV_FILE_TEST, INPUT_FOLDER
from EA_Engine import EA_Engine
from utils.DataModels import Song


def main():
    logger = Logger()
    engine = EA_Engine(logger)

    song1 = Song.from_wav_file(WAV_FILE_TEST, duration=30)
    song2 = Song.from_wav_file(os.path.join(INPUT_FOLDER, "bohemian_raphsody.wav"), duration=30)

    results = engine.mix(song1, song2, popsize=5)
    for i in range(len(results)):
        sf.write(f"{INPUT_FOLDER}/result_{i}.wav", results[i].data, results[i].sr)


if __name__ == "__main__":
    main()
