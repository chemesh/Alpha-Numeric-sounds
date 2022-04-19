from deap import base, creator, tools
import mingus
import librosa
import matplotlib.pyplot as plt




from constants import WAV_FILE_TEST


def main():
    data, samplerate = librosa.load(WAV_FILE_TEST)
    print(f"data: {data}, sample rate: {samplerate}")

    hop_length = 512
    h_data, p_data = librosa.effects.hpss(data)
    print(f"decomposition values - \nHarmonic data: {h_data}\n Percussive data: {p_data}")

    tempo, beat_frames = librosa.beat.beat_track(y=p_data, sr=samplerate)
    print(f"tempo: {tempo:.2f}")

    beat_times = librosa.frames_to_time(beat_frames, sr=samplerate)
    print(f"beat times: {beat_times}")


if __name__ == "__main__":
    main()
