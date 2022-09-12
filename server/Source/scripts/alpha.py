import os

import soundfile as sf
import librosa
from server.Source.utils.Logger import Logger
from server.Source.utils.Constants import WAV_FILE_TEST, INPUT_FOLDER
from EA_Engine import EA_Engine
from server.Source.utils.DataModels import Song
import server.Source.utils.SoundUtils as su
import server.Source.utils.Constants as consts


def main():
    logger = Logger()
    #engine = EA_Engine(logger)

    song1 = Song.from_wav_file(f'{consts.INPUT_FOLDER}/dancingwiththemoon.wav')
    print(f'song data - {song1.data}, duration = {song1.duration}')
    layers = su.separate_voices(song1.data)
    sf.write(f"{INPUT_FOLDER}/moon_drums.wav", layers[su.INSTRUMENT.DRUMS.value], song1.sr)
    sf.write(f"{INPUT_FOLDER}/moon_vocals.wav", layers[su.INSTRUMENT.VOCALS.value], song1.sr)
    sf.write(f"{INPUT_FOLDER}/moon_bass.wav", layers[su.INSTRUMENT.BASS.value], song1.sr)

    # song2 = Song.from_wav_file(f'{consts.INPUT_FOLDER}/lastmilehome.wav', duration=60)
    # song2.data, _ = librosa.effects.trim(song2.data)
    # song1.data, _ = librosa.effects.trim(song1.data)
    # su.adjust_bpm(song1, song2)
    # sf.write(f"{INPUT_FOLDER}/song1_after.wav", song1.data, song1.sr)
    # sf.write(f"{INPUT_FOLDER}/song2_after.wav", song2.data, song2.sr)
    # logger.info('saved original files after adjustment...')
    # timed_segs_1, bkps_1 = su.break_to_timed_segments(song1.data, song1.sr)
    # timed_segs_2, bkps_2 = su.break_to_timed_segments(song2.data, song2.sr)
    # mix = su.rand_reconstruct(song1.data, song1.sr, song2.data, song2.sr, inst=su.INSTRUMENT.VOCALS)
    # logger.info('finished 1st reconstruction...')
    # sf.write(f"{INPUT_FOLDER}/0_result_test.wav", mix, song1.sr)
    # logger.info('saved first mix...')
    # mix1 = su.rand_reconstruct(song1.data, song1.sr, song2.data, song2.sr, inst=su.INSTRUMENT.VOCALS)
    # logger.info('finished 2nd reconstruction...')
    # sf.write(f"{INPUT_FOLDER}/1_test.wav", mix1, song1.sr)
    # logger.info('saved second mix...')
    # mix2 = su.rand_reconstruct(mix, song1.sr, mix1, song2.sr, inst=su.INSTRUMENT.VOCALS)
    # logger.info('finished 3rd reconstruction...')
    # sf.write(f"{INPUT_FOLDER}/result_test.wav", mix2, song1.sr)
    # logger.info('saved final mix...')

    # 1TODO before mixing the 2 original songs, adjust their bpms and

    #results = engine.mix(song1, song2, popsize=5)
    #for i in range(len(results)):
    #    sf.write(f"{INPUT_FOLDER}/result_{i}.wav", results[i].data, results[i].sr)


if __name__ == "__main__":
    main()
