import enum
import numpy as np
import random
import librosa
import ruptures as rpt
# import matplotlib.pyplot as plt
from typing import List, Tuple, Any
import math
from server.Source.utils.SingletonSeperator import SingleSeperator

from server.Source.utils.Constants import MAX_BKPS

class INSTRUMENT(enum.Enum):
    BASS = "bass"
    DRUMS = "drums"
    PIANO = "piano"
    VOCALS = "vocals"
    OTHER = "other"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))



def denoise(y: np.ndarray, min_db_ratio: float) -> np.ndarray:
    """
    :param y: time-series data
    :param min_db_ratio: positive float (0-1). 0 will not filter out anything, while 1 will return an array of 0's
    :return: noise-filtered time-series data
    """
    stft = librosa.stft(y)
    stft_db = librosa.amplitude_to_db(np.abs(stft), ref=np.max)
    mask = stft_db > (min_db_ratio * np.min(stft_db))
    return librosa.istft(stft * mask)


def rand_reconstruct(
        data1: np.ndarray,
        sr1: int,
        data2: np.ndarray,
        sr2: int,
        inst: INSTRUMENT = None,
        hop_length: int = 256
) -> Any:
    bkps1 = np.pad(
        array=partition(data1, sr1, MAX_BKPS, hop_length=hop_length, in_ms=True),
        pad_width=(1, 0),
        constant_values=0
    )
    bkps2 = np.pad(
        array=partition(data2, sr2, MAX_BKPS, hop_length=hop_length, in_ms=True),
        pad_width=(1, 0),
        constant_values=0
    )

    # bkps = [0, t0, t1, t2, ..., tn, len(song)] such that ti is the timestamp for ith possible breakpoint in the song
    idx1 = random.randrange(len(bkps1)-1)
    idx2 = random.randrange(len(bkps2)-1)

    # randomize which function to use between "swap" and "overlay"
    no_change = random.choice([True, False])
    if random.choice(["swap", "overlay"]) == "swap":
        new_data, _ = swap(
            data1=data1,
            sr1=sr1,
            data2=data2,
            sr2=sr2,
            d1_start_ms=bkps1[idx1],
            d1_end_ms=bkps1[idx1 + 1],
            d2_start_ms=bkps2[idx2],
            d2_end_ms=bkps2[idx2 + 1],
            inst=inst
        ) if no_change else swap(
            data1=data2,
            sr1=sr2,
            data2=data1,
            sr2=sr1,
            d1_start_ms=bkps2[idx2],
            d1_end_ms=bkps2[idx2 + 1],
            d2_start_ms=bkps1[idx1],
            d2_end_ms=bkps1[idx1 + 1],
            inst=inst
        )
    else:
        new_data, _ = overlay(
            data1=data1,
            sr1=sr1,
            data2=data2[ms_to_frame(bkps2[idx2], sr2):ms_to_frame(bkps2[idx2+1], sr2)],
            sr2=sr2,
            start_ms=bkps1[idx1],
            inst=inst
        ) if no_change else overlay(
            data1=data2,
            sr1=sr2,
            data2=data1[ms_to_frame(bkps1[idx1], sr1):ms_to_frame(bkps1[idx1+1], sr1)],
            sr2=sr1,
            start_ms=bkps2[idx2],
            inst=inst
        )
    return new_data


def extract_voice(data: np.ndarray, sr: int, inst: INSTRUMENT) -> Tuple[np.ndarray, np.ndarray]:
    """
    extract the voice of certain instrument from data
    :return: tuple where first value is the extracted voice,
    and second value is the original data without the extracted voice
    """
    voices = separate_voices(data)
    voice_to_extract = voices.pop(inst)

    new_data = voices.popitem()[1]
    while voices:
        new_data, _ = combine(new_data, sr, voices.popitem()[1], sr)

    return voice_to_extract, new_data


def ms_to_frame(ts: int, sr: int):
    return sr * ts // 1000


def overlay(
        data1: np.ndarray,
        sr1: int,
        data2: np.ndarray,
        sr2: int,
        start_ms: int = 0,
        inst: INSTRUMENT = None
) -> Tuple[np.ndarray, int]:
    sub = np.array_split(data1, [ms_to_frame(start_ms, sr1)])
    combined, sr = combine(sub[1], sr1, data2, sr2, inst)
    return np.append(sub[0], combined), sr


def combine(
        data1: np.ndarray,
        sr1: int,
        data2: np.ndarray,
        sr2: int,
        inst: INSTRUMENT = None
) -> Tuple[np.ndarray, int]:

    if inst:
        data2, _ = extract_voice(data2, sr2, inst)

    if data1.shape[0] > data2.shape[0]:
        data2 = np.pad(data2, (0, data1.shape[0]-data2.shape[0]), "constant")
    elif data1.shape[0] < data2.shape[0]:
        data1 = np.pad(data1, (0, data2.shape[0] - data1.shape[0]), "constant")

    return (data1 + data2) / 2, (sr1 + sr2) // 2


def swap(
        data1: np.ndarray,
        sr1: int,
        data2: np.ndarray,
        sr2: int,
        d1_start_ms: int,
        d1_end_ms: int,
        d2_start_ms: int,
        d2_end_ms: int,
        inst: INSTRUMENT = None
) -> Tuple[np.ndarray, np.ndarray]:

    d1_start_idx = ms_to_frame(d1_start_ms, sr1)
    d1_end_idx = ms_to_frame(d1_end_ms, sr1)
    d2_start_idx = ms_to_frame(d2_start_ms, sr2)
    d2_end_idx = ms_to_frame(d2_end_ms, sr2)

    part1 = data1[d1_start_idx:d1_end_idx]
    part2 = data2[d2_start_idx:d2_end_idx]

    if inst:
        inst1, back1 = extract_voice(data1, sr1, inst)
        inst2, back2 = extract_voice(data2, sr2, inst)
        part1 = combine(inst1, sr1, back2, sr2)
        part2 = combine(inst2, sr2, back1, sr1)

    new_data1 = np.insert(np.delete(data1, slice(d1_start_idx, d1_end_idx)), d1_start_idx, part2)
    new_data2 = np.insert(np.delete(data2, slice(d2_start_idx, d2_end_idx)), d2_start_idx, part1)
    return new_data1, new_data2


def get_sum_of_cost(algo: rpt.KernelCPD, n_bkps: int) -> float:
    """Return the sum of costs for the change points `bkps`"""
    bkps = algo.predict(n_bkps=n_bkps)
    return algo.cost.sum_of_costs(bkps)


def optimal_bkps(bkps_costs: List) -> int:
    max_pos = 1
    max_angle = None

    for bkp_pos in range(1, len(bkps_costs) - 1):
        # given point b:(x_i,y_i), we will find the angle between a:(x_i-1,y_i-1) and c:(x-i+1,y_i+1)
        # going through point b
        angle = compute_angle(bkp_pos - 1, bkps_costs[bkp_pos - 1],
                              bkp_pos, bkps_costs[bkp_pos],
                              bkp_pos + 1, bkps_costs[bkp_pos + 1])
        if not max_angle:
            max_angle = angle
            continue
        if angle < max_angle:
            max_angle = angle
            max_pos = bkp_pos
            # print(f"max_pos: {max_pos}, max_angle: {max_angle}")
    return max_pos


def compute_angle(x1, y1, x2, y2, x3, y3):
    m1 = delta1 = (y2 - y1) / (x2 - x1)    # first incline
    m2 = delta2 = (y3 - y2) / (x3 - x2)    # second incline
    angl_tan = (m2 - m1) / (1 + m2 * m1)
    print(angl_tan)
    angle = math.atan(angl_tan)
    #angle = np.degrees(np.arccos(np.dot(delta1, delta2) / (np.linalg.norm(delta1) * np.linalg.norm(delta2))))
    print(f"angle between n_bkps: {x1}, {x2}, {x3}: {angle}")
    return angle


def separate_voices(data: np.ndarray, as_mono=True):
    def to_mono(ary: np.ndarray):
        a, b = np.split(ary, 2, axis=-1)
        mono = (a + b) / 2
        return mono.reshape(data.shape[0])

    data = data.reshape(data.shape[0], 1)
    voices = SingleSeperator().separate(data)
    processed_voices = {n: to_mono(v) for n, v in voices.items()} if as_mono else voices
    return processed_voices


def get_clean_freq(data: np.ndarray):
    n = data.shape[-1]
    f = np.fft.fft(data, n)
    psd = f * np.conj(f) / n
    ind = psd > np.average(psd)
    return np.fft.ifft(ind * f)


# def fig_ax(figsize=(15, 5), dpi=150):
#     """Return a (matplotlib) figure and ax objects with given size."""
#     return plt.subplots(figsize=figsize, dpi=dpi)


def partition(data: np.ndarray, samplerate: int, n_bkps_max: int, hop_length: int = 256, in_ms: bool = False) -> List:
    # Compute the onset strength
    oenv = librosa.onset.onset_strength(
        y=data, sr=samplerate, hop_length=hop_length
    )
    # Compute the tempogram
    tempogram = librosa.feature.tempogram(
        onset_envelope=oenv,
        sr=samplerate,
        hop_length=hop_length)

    # Choose detection method
    algo = rpt.KernelCPD(kernel="linear").fit(tempogram.T)

    # Choose the number of changes (elbow heuristic)
    # Start by computing the segmentation with most changes.
    # After start, all segmentations with 1, 2,..., K_max-1 changes are also available for free.
    _ = algo.predict(n_bkps_max)

    array_of_n_bkps = np.arange(1, n_bkps_max + 1)
    bkps_costs = [get_sum_of_cost(algo=algo, n_bkps=n_bkps) for n_bkps in array_of_n_bkps]
    print(f'sum of cost array y values: {bkps_costs}')

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
    # plt.show()

    n_bkps = optimal_bkps(bkps_costs)
    print(f"n_bkps: {n_bkps}")

    # Segmentation
    bkps = algo.predict(n_bkps=n_bkps+5)   # HARD CODED ADDITION OF BKPS! Notice
    # Convert the estimated change points (frame counts) to actual timestamps
    bkps_times = librosa.frames_to_time(bkps, sr=samplerate, hop_length=hop_length)
    if in_ms:
        bkps_times *= 1000
        bkps_times = bkps_times.astype("int32")
    return bkps_times

    # bkps_time_indexes = (samplerate * bkps_times).astype(int).tolist()
    # segments = [data[start:end] for (segment_number, (start, end)) in
    #             enumerate(rpt.utils.pairwise([0] + bkps_time_indexes), start=1)]
    # return segments
