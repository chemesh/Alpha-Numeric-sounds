import librosa
import soundfile as sf
import numpy as np
import Raters.raters as rating

import utils.SoundUtils as su


def main():
    y1, sr1 = librosa.load(librosa.ex("vibeace"), offset=10., duration=15)


    voices = su.separate_voices(y1)

    filtered_freq = su.clean_wave(voices["piano"])
    # print(f'type of filtered_freq: {type(filtered_freq)}')
    print(f'filtered_freq value= {filtered_freq}')
    notes = librosa.hz_to_note(np.trim_zeros(filtered_freq))
    print(notes)
    print(f'first rater value: {rating.sub_rater_neighbooring_pitch(notes)}')
    # print(f"freq: {freq}")


if __name__ == "__main__":
    main()
