from deap import base, creator, tools
import mingus
import librosa
import matplotlib.pyplot as plt
import numpy as np
from librosa import display



from constants import WAV_FILE_TEST


def main():
    data, samplerate = librosa.load(WAV_FILE_TEST)
    print(f"data: {data}, sample rate: {samplerate}")

    tempo, beat_frames = librosa.beat.beat_track(y=data, sr=samplerate)
    print(f"tempo: {tempo:.2f}")

    beat_times = librosa.frames_to_time(beat_frames, sr=samplerate)
    print(f"beat times: {beat_times}")

    d = librosa.stft(data)
    h, p = librosa.decompose.hpss(d)
    print(f"decomposition values - \nH: {h}\n P: {p}")

    fig, ax = plt.subplots(nrows=3, sharex=True, sharey=True)
    img = librosa.display.specshow(librosa.amplitude_to_db(np.abs(d),
                                                           ref=np.max),
                                   y_axis='log', x_axis='time', ax=ax[0])
    ax[0].set(title='Full power spectrogram')
    ax[0].label_outer()
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(h),
                                                     ref=np.max(np.abs(d))),
                             y_axis='log', x_axis='time', ax=ax[1])
    ax[1].set(title='Harmonic power spectrogram')
    ax[1].label_outer()
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(p),
                                                     ref=np.max(np.abs(p))),
                             y_axis='log', x_axis='time', ax=ax[2])
    ax[2].set(title='Percussive power spectrogram')
    fig.colorbar(img, ax=ax, format='%+2.0f dB')
    fig.show()



if __name__ == "__main__":
    main()
