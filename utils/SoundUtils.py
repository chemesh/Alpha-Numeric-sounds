import enum
import numpy as np
import random
import librosa
import librosa.display
import ruptures as rpt
from spleeter.separator import Separator
from typing import List, Tuple, Dict, Any
import re

from utils.Constants import MAX_BKPS


class INSTRUMENT(enum.Enum):
    BASS = "bass"
    DRUMS = "drums"
    PIANO = "piano"
    VOCALS = "vocals"
    OTHER = "other"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


def rand_reconstruct(data1: np.ndarray, sr1: int, data2: np.ndarray, sr2: int, hop_length: int = 256) -> Any:
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
    if random.choice(["swap", "overlay"]) == "swap":
        new_data, _ = swap(
            data1=data1,
            sr1=sr1,
            data2=data2,
            sr2=sr2,
            d1_start_ms=bkps1[idx1],
            d1_end_ms=bkps1[idx1 + 1],
            d2_start_ms=bkps2[idx2],
            d2_end_ms=bkps2[idx2 + 1]
        )
    else:
        new_data, _ = overlay(
            data1=data1,
            sr1=sr1,
            data2=data2[ms_to_frame(bkps2[idx2], sr2):ms_to_frame(bkps2[idx2+1], sr2)],
            sr2=sr2,
            start_ms=bkps1[idx1]
        )
    return new_data


def extract_voice(data: np.ndarray, sr: int, inst: INSTRUMENT) -> Tuple[np.ndarray, np.ndarray]:
    """
    extract the voice of certain instrument from data
    :return: tuple where first value is the extracted voice,
    and second value is the original data without the extracted voice
    """
    voices = separate_voices(data)
    voice_to_extract = voices.pop(inst.value)

    new_data = voices.popitem()[1]
    while voices:
        new_data, _ = combine(new_data, sr, voices.popitem()[1], sr)

    return voice_to_extract, new_data


def ms_to_frame(ts: int, sr: int):
    return sr * ts // 1000


def overlay(data1: np.ndarray, sr1: int, data2: np.ndarray, sr2: int, start_ms: int = 0) -> Tuple[np.ndarray, int]:
    sub = np.array_split(data1, [ms_to_frame(start_ms, sr1)])
    combined, sr = combine(sub[1], sr1, data2, sr2)
    return np.append(sub[0], combined), sr


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

    d1_start_idx = ms_to_frame(d1_start_ms, sr1)
    d1_end_idx = ms_to_frame(d1_end_ms, sr1)
    d2_start_idx = ms_to_frame(d2_start_ms, sr2)
    d2_end_idx = ms_to_frame(d2_end_ms, sr2)

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


def separate_voices(data: np.ndarray):
    return Separator("spleeter:5stems").separate(data.reshape(data.shape[0], 1))


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

    # Visually we choose n_bkps=5 (highlighted in red on the elbow plot)
    n_bkps = optimal_bkps(bkps_costs)

    # Segmentation
    bkps = algo.predict(n_bkps=n_bkps)
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

def to_mingus_form(note):
    '''
    converts xi to x-i. for example: A8 -> A-8, B#4 -> B#-4
    '''
    return re.sub(r'([^0-9])([0-9])', r'\1-\2', re.sub(r'([^A-Z0-9])', '#', note))