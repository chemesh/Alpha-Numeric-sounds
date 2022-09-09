import soundfile as sf

from Source.utils.Logger import Logger
from Source.utils.Constants import OUTPUT_FOLDER
from Source.scripts.EA_Engine import EA_Engine
from Source.utils.DataModels import Song


def start(paths, exec_id):
    logger = Logger()
    engine = EA_Engine(logger)

    songs = [Song.from_wav_file(path) for path in paths]
    results = engine.mix(*songs, popsize=5)
    sf.write(f"{OUTPUT_FOLDER}/result_{exec_id}.wav", results[0].data, results[0].sr)

    return OUTPUT_FOLDER

