import librosa
import librosa.display
import soundfile as sf
import matplotlib.pyplot as plt
import numpy as np
from spleeter.separator import Separator

from utils.Logger import Logger
from utils.Constants import WAV_FILE_TEST, INPUT_FOLDER
from EA_Engine import EA_Engine
from utils.DataModels import Song


def main():
    logger = Logger()
    # engine = EA_Engine()
    sep = Separator("spleeter:5stems")

    # data, samplerate = librosa.load(librosa.ex('trumpet'))
    # data, samplerate = librosa.load(librosa.ex('nutcracker'))
    # song1 = Song(WAV_FILE_TEST)
    song1 = Song(WAV_FILE_TEST, duration=60.0)
    song2 = Song(librosa.ex('nutcracker'))
    # mp3_to_wav(str(Path(INPUT_FOLDER)/"In-the-hall-of-the-mountain-king.mp3"))
    # wav_file = str(Path(INPUT_FOLDER)/"In-the-hall-of-the-mountain-king.wav")
    # data, samplerate = librosa.load(wav_file)

    # results = engine.mix(song1, song2)

    from spleeter.audio.adapter import AudioAdapter

    audio_loader = AudioAdapter.default()
    waveform, sr = audio_loader.load(WAV_FILE_TEST, sample_rate=22050)

    # logger.info(f"data: {song1.data}, sample rate: {song1.sr}")
    logger.info(f"type: {waveform.dtype}")
    logger.info(f"size: {len(waveform)*64}")

    song1_parts = sep.separate(waveform)
    for inst, data in song1_parts.items():
        logger.info(f"instrument: {inst}, data:{data}")
        sf.write(f"{INPUT_FOLDER}/{inst}.wav", data, int(sr))

    # hop_length = 512
    # h_data, p_data = librosa.effects.hpss(song1.data)
    # logger.debug(f"decomposition values - \nHarmonic data: {h_data}\n Percussive data: {p_data}")
    #
    # tempo, beat_frames = librosa.beat.beat_track(y=p_data, sr=song1.sr)
    # logger.warn(f"tempo: {tempo:.2f}")
    #
    # beat_times = librosa.frames_to_time(beat_frames, sr=song1.sr)
    # logger.error(f"beat times: {beat_times}")
    #
    # # segments = partition(data, samplerate)
    #
    # # segment_freq = [librosa.stft(part) for part in segments]
    #
    # freq = librosa.stft(song1.data)
    # print(f"freq: {freq}")
    # mag, phase = librosa.magphase(freq)
    # print(f"mag: {mag}")
    # print(f"phase: {phase}")
    #
    # S_filter = librosa.decompose.nn_filter(mag,
    #                                        aggregate=np.median,
    #                                        metric='cosine',
    #                                        width=int(librosa.time_to_frames(2, sr=song1.sr)))
    #
    # # The output of the filter shouldn't be greater than the input
    # # if we assume signals are additive.  Taking the pointwise minimum
    # # with the input spectrum forces this.
    # S_filter = np.minimum(mag, S_filter)
    #
    # # We can also use a margin to reduce bleed between the vocals and instrumentation masks.
    # # Note: the margins need not be equal for foreground and background separation
    # margin_i, margin_v = 1, 10
    # power = 2
    #
    # mask_i = librosa.util.softmask(S_filter,
    #                                margin_i * (mag - S_filter),
    #                                power=power)
    #
    # mask_v = librosa.util.softmask(mag - S_filter,
    #                                margin_v * S_filter,
    #                                power=power)
    #
    # mask_back = librosa.util.softmask(S_filter,
    #                                   mag - S_filter,
    #                                   power=power)
    #
    # mask_lead = librosa.util.softmask(mag - S_filter,
    #                                   S_filter,
    #                                   power=power)
    #
    # # Once we have the masks, simply multiply them with the input spectrum
    # # to separate the components
    #
    # S_foreground = mask_v * mag
    # S_background = mask_back * mag
    #
    # fig, ax = plt.subplots(nrows=3, sharex=True, sharey=True)
    # img = librosa.display.specshow(librosa.amplitude_to_db(mag, ref=np.max),
    #                                y_axis='log', x_axis='time', sr=song1.sr, ax=ax[0])
    # ax[0].set(title='Full spectrum')
    # ax[0].label_outer()
    #
    # librosa.display.specshow(librosa.amplitude_to_db(S_background, ref=np.max),
    #                          y_axis='log', x_axis='time', sr=song1.sr, ax=ax[1])
    # ax[1].set(title='Background')
    # ax[1].label_outer()
    #
    # librosa.display.specshow(librosa.amplitude_to_db(S_foreground, ref=np.max),
    #                          y_axis='log', x_axis='time', sr=song1.sr, ax=ax[2])
    # ax[2].set(title='Foreground')
    # fig.colorbar(img, ax=ax)
    # fig.show()
    #
    # foreground = librosa.istft(S_foreground * phase)
    # background = librosa.istft(S_background * phase)
    #
    # sf.write(f"{INPUT_FOLDER}/foreground.wav", foreground, song1.sr)
    # sf.write(f"{INPUT_FOLDER}/background.wav", background, song1.sr)
    #
    # # notes = librosa.hz_to_note(freq)
    # # logger.info(f"notes: {notes[:5][:5]}")
    #


if __name__ == "__main__":
    main()
