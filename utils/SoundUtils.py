from typing import List, Tuple

import librosa
import librosa.display
import ruptures as rpt
import numpy as np


def combine(data1: np.ndarray, sr1: int, data2: np.ndarray, sr2: int) -> Tuple[np.ndarray, int]:
    if data1.shape[0] > data2.shape[0]:
        data2 = np.pad(data2, (0, data1.shape[0]-data2.shape[0]), "constant")
    elif data1.shape[0] < data2.shape[0]:
        data1 = np.pad(data1, (0, data2.shape[0] - data1.shape[0]), "constant")

    return (data1 + data2) / 2, int((sr1 + sr2) / 2)


def swap(
        data1: np.ndarray,
        sr1: int,
        data2: np.ndarray,
        sr2: int,
        d1_start_ms: int,
        d1_end_ms: int,
        d2_start_ms: int,
        d2_end_ms: int
) -> Tuple[np.ndarray, np.ndarray]:

    d1_start_idx = sr1 * d1_start_ms // 1000
    d1_end_idx = sr1 * d1_end_ms // 1000
    d2_start_idx = sr2 * d2_start_ms // 1000
    d2_end_idx = sr2 * d2_end_ms // 1000

    part1 = data1[d1_start_idx:d1_end_idx]
    part2 = data2[d2_start_idx:d2_end_idx]
    new_data1 = np.insert(np.delete(data1, slice(d1_start_idx, d1_end_idx)), d1_start_idx, part2)
    new_data2 = np.insert(np.delete(data2, slice(d2_start_idx, d2_end_idx)), d2_start_idx, part1)
    return new_data1, new_data2


def get_sum_of_cost(algo: rpt.KernelCPD, n_bkps: int) -> float:
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
