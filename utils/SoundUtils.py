from typing import List

import librosa
import librosa.display
import ruptures as rpt
from pydub import AudioSegment
import numpy as np
import io
import scipy.io.wavfile


def as_to_ndarr(sound: AudioSegment) -> np.ndarray:
    channel_sounds = sound.set_frame_rate(16000).split_to_mono()
    samples = [s.get_array_of_samples() for s in channel_sounds]
    fp_arr = np.array(samples).T.astype(np.float32)
    fp_arr /= np.iinfo(samples[0].typecode).max
    return fp_arr


def ndarr_to_as(arr: np.ndarray) -> AudioSegment:
    wav_io = io.BytesIO()
    scipy.io.wavfile.write(wav_io, 16000, arr)
    wav_io.seek(0)
    seg = AudioSegment.from_wav(wav_io)
    return seg


def get_sum_of_cost(algo, n_bkps) -> float:
    """Return the sum of costs for the change points `bkps`"""
    bkps = algo.predict(n_bkps=n_bkps)
    return algo.cost.sum_of_costs(bkps)


def optimal_bkps(bkps_costs: List) -> int:
    max_pos = 1
    max_delta = 0
    for bkp_pos in range(1, len(bkps_costs) - 1):
        delta1 = bkps_costs[bkp_pos - 1] - bkps_costs[bkp_pos]
        delta2 = bkps_costs[bkp_pos] - bkps_costs[bkp_pos + 1]
        print(f"curr pos: {bkp_pos}, delta: {delta1 - delta2}")
        if delta1 - delta2 > max_delta:
            max_delta = delta1 - delta2
            max_pos = bkp_pos
    return max_pos + 1


def partition(data: np.ndarray, samplerate: int, logger) -> List:
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
    bkps_costs = [get_sum_of_cost(algo=algo, n_bkps=n_bkps) for n_bkps in array_of_n_bkps]
    logger.info(f"bkps_costs -  type: {type(bkps_costs)},\ndata: {bkps_costs}")

    # fig, ax = fig_ax((7, 4))
    # ax.plot(
    #     array_of_n_bkps,
    #     bkps_costs,
    #     "-*",
    #     alpha=0.5,
    # )
    # ax.set_xticks(array_of_n_bkps)
    # ax.set_xlabel("Number of change points")
    # ax.set_title("Sum of costs")
    # ax.grid(axis="x")
    # ax.set_xlim(0, n_bkps_max + 1)
    # fig.show()

    # Visually we choose n_bkps=5 (highlighted in red on the elbow plot)
    # n_bkps = optimal_bkps(bkps_costs)
    n_bkps = optimal_bkps()
    logger.info(f"optimal number of breakpoints is: {n_bkps}")
    # _ = ax.scatter([5], [get_sum_of_cost(algo=algo, n_bkps=n_bkps)], color="r", s=100)

    # Segmentation
    bkps = algo.predict(n_bkps=n_bkps)
    # Convert the estimated change points (frame counts) to actual timestamps
    bkps_times = librosa.frames_to_time(bkps, sr=samplerate, hop_length=hop_length_tempo)
    logger.info(f"bkps_times {bkps_times}")

    bkps_time_indexes = (samplerate * bkps_times).astype(int).tolist()

    segments = [data[start:end] for (segment_number, (start, end)) in
                enumerate(rpt.utils.pairwise([0] + bkps_time_indexes), start=1)]
    return segments
