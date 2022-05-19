import librosa
import librosa.display
import soundfile
from pydub import AudioSegment
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import deap

from utils.Logger import Logger
from utils.constants import WAV_FILE_TEST, INPUT_FOLDER
from utils.sound_utils import partition


def fig_ax(figsize=(15, 5), dpi=150):
    """Return a (matplotlib) figure and ax objects with given size."""
    return plt.subplots(figsize=figsize, dpi=dpi)




def mp3_to_wav(mp3_path):
    sound = AudioSegment.from_mp3(mp3_path)
    filename = Path(mp3_path).name + ".wav"
    sound.export(str(Path(INPUT_FOLDER)/filename), format="wav")

def main():
    logger = Logger()
    data, samplerate = librosa.load(librosa.ex('trumpet'))
    # data, samplerate = librosa.load(WAV_FILE_TEST)
    # mp3_to_wav(str(Path(INPUT_FOLDER)/"In-the-hall-of-the-mountain-king.mp3"))
    # wav_file = str(Path(INPUT_FOLDER)/"In-the-hall-of-the-mountain-king.wav")
    # data, samplerate = librosa.load(wav_file)
    logger.info(f"data: {data}, sample rate: {samplerate}")

    hop_length = 512
    h_data, p_data = librosa.effects.hpss(data)
    logger.debug(f"decomposition values - \nHarmonic data: {h_data}\n Percussive data: {p_data}")

    tempo, beat_frames = librosa.beat.beat_track(y=p_data, sr=samplerate)
    logger.warn(f"tempo: {tempo:.2f}")

    beat_times = librosa.frames_to_time(beat_frames, sr=samplerate)
    logger.error(f"beat times: {beat_times}")

    # segments = partition(data, samplerate)
    #
    # segment_freq = [librosa.stft(part) for part in segments]
    freq = librosa.stft(data)
    print(f"freq: {freq}")
    mag, phase = librosa.magphase(freq)
    print(f"mag: {mag}")
    print(f"phase: {phase}")
    # notes = librosa.hz_to_note(freq)
    # logger.info(f"notes: {notes[:5][:5]}")







if __name__ == "__main__":
    main()
