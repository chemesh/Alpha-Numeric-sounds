import os

import soundfile as sf
import librosa
from Source.utils.Logger import Logger
from Source.utils.Constants import WAV_FILE_TEST, INPUT_FOLDER
from EA_Engine import EA_Engine
from Source.utils.DataModels import Song


def main():
    logger = Logger()
    engine = EA_Engine(logger)

    song1 = Song.from_wav_file(WAV_FILE_TEST, duration=30)
    song2 = Song.from_wav_file(os.path.join(INPUT_FOLDER, "bohemian_raphsody.wav"), duration=30)

    # 1TODO before mixing the 2 original songs, adjust their bpms and

    results = engine.mix(song1, song2, popsize=5)
    for i in range(len(results)):
        sf.write(f"{INPUT_FOLDER}/result_{i}.wav", results[i].data, results[i].sr)


if __name__ == "__main__":
    main()
