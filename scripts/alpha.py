import librosa
import librosa.display
from utils.Logger import Logger
from utils.constants import WAV_FILE_TEST
import ruptures as rpt
import matplotlib.pyplot as plt
import numpy as np


def fig_ax(figsize=(15, 5), dpi=150):
    """Return a (matplotlib) figure and ax objects with given size."""
    return plt.subplots(figsize=figsize, dpi=dpi)

def get_sum_of_cost(algo, n_bkps) -> float:
    """Return the sum of costs for the change points `bkps`"""
    bkps = algo.predict(n_bkps=n_bkps)
    return algo.cost.sum_of_costs(bkps)


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

    # Compute the onset strength
    hop_length_tempo = 256
    oenv = librosa.onset.onset_strength(
        y=data, sr=samplerate, hop_length=hop_length_tempo
    )
    # Compute the tempogram
    tempogram = librosa.feature.tempogram(
        onset_envelope=oenv,
        sr=samplerate,
        hop_length=hop_length_tempo)

    # Choose detection method
    algo = rpt.KernelCPD(kernel="linear").fit(tempogram.T)

    # Choose the number of changes (elbow heuristic)
    n_bkps_max = 10  # K_max
    # Start by computing the segmentation with most changes.
    # After start, all segmentations with 1, 2,..., K_max-1 changes are also available for free.
    _ = algo.predict(n_bkps_max)

    array_of_n_bkps = np.arange(1, n_bkps_max + 1)
    logger.info(f"array_of_n_bkps -  type: {type(array_of_n_bkps)},\ndata: {array_of_n_bkps}")

    fig, ax = fig_ax((7, 4))
    ax.plot(
        array_of_n_bkps,
        [get_sum_of_cost(algo=algo, n_bkps=n_bkps) for n_bkps in array_of_n_bkps],
        "-*",
        alpha=0.5,
    )
    ax.set_xticks(array_of_n_bkps)
    ax.set_xlabel("Number of change points")
    ax.set_title("Sum of costs")
    ax.grid(axis="x")
    ax.set_xlim(0, n_bkps_max + 1)
    fig.show()

    # Visually we choose n_bkps=5 (highlighted in red on the elbow plot)
    n_bkps = 2
    _ = ax.scatter([5], [get_sum_of_cost(algo=algo, n_bkps=5)], color="r", s=100)

    # Segmentation
    bkps = algo.predict(n_bkps=n_bkps)
    # Convert the estimated change points (frame counts) to actual timestamps
    bkps_times = librosa.frames_to_time(bkps, sr=samplerate, hop_length=hop_length_tempo)
    logger.info(f"bkps_times {bkps_times}")

    bkps_time_indexes = (samplerate * bkps_times).astype(int).tolist()

    segments = [data[start:end] for (segment_number, (start, end)) in enumerate(rpt.utils.pairwise([0] + bkps_time_indexes), start=1)]

if __name__ == "__main__":
    main()
