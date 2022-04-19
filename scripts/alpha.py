import librosa
from utils.Logger import Logger
from utils.constants import WAV_FILE_TEST


def main():
    logger = Logger()
    data, samplerate = librosa.load(WAV_FILE_TEST)
    logger.info(f"data: {data}, sample rate: {samplerate}")

    hop_length = 512
    h_data, p_data = librosa.effects.hpss(data)
    logger.debug(f"decomposition values - \nHarmonic data: {h_data}\n Percussive data: {p_data}")

    tempo, beat_frames = librosa.beat.beat_track(y=p_data, sr=samplerate)
    logger.warn(f"tempo: {tempo:.2f}")

    beat_times = librosa.frames_to_time(beat_frames, sr=samplerate)
    logger.error(f"beat times: {beat_times}")


if __name__ == "__main__":
    main()
