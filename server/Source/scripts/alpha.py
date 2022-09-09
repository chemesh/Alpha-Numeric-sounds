import soundfile as sf

from Source.utils.Logger import Logger
from Source.utils.Constants import OUTPUT_FOLDER
from Source.scripts.EA_Engine import EA_Engine
from Source.utils.DataModels import Song


def start(paths):
    logger = Logger()
    engine = EA_Engine(logger)

    songs = [Song.from_wav_file(path) for path in paths]
    results = engine.mix(*songs, popsize=5)
    for i in range(len(results)):
        sf.write(f"{OUTPUT_FOLDER}/result_{i}.wav", results[i].data, results[i].sr)

    return OUTPUT_FOLDER

