import enum
import re
import numpy as np
import random
import librosa
import librosa.display
import ruptures as rpt
import matplotlib.pyplot as plt
import math

from typing import List, Tuple, Any
from mingus.containers import Note
from mingus.core import intervals, keys
from spleeter.separator import Separator

from Source.utils.Logger import Logger as log
from Source.utils.Constants import MAX_BKPS, INPUT_FOLDER
from Source.utils.keydin import pitchdistribution as pd, classifiers
from Source.utils.DataModels import Song



class INSTRUMENT(enum.Enum):
    BASS = "bass"
    DRUMS = "drums"
    PIANO = "piano"
    VOCALS = "vocals"
    OTHER = "other"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class SCALE_TYPE(enum.Enum):
    major = "major"
    minor = "minor"
    diatonic = "diatonic"


KEYS = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

# TODOp:
#  adjust BPM of all individuals! (stretch all to max / smoosh all to min with given probability)
#  adjust pitch!
#

def adjust_bpm(song1:Song, song2:Song):
    """
    if songs tempo doesn't match, speeds up the "slower" one to match the "faster"
    """
    bpm1 = song1.tempo
    bpm2 = song2.tempo
    if bpm1 > bpm2:
        song2.data = librosa.effects.time_stretch(song2.data, bpm1/bpm2)
    elif bpm2 > bpm1:
        song1.data = librosa.effects.time_stretch(song1.data, bpm2/bpm1)
    return


def adjust_pitch(song1:Song, song2:Song):
    if song1.key == song2.key:
        return
    maj = 'maj'
    min = 'min'
    first_clean_key = song1.key.split(' ')[0]
    second_clean_key = song2.key.split(' ')[0]
    if (maj in song1.key and maj in song2.key) or (min in song1.key and min in song2.key):
        if first_clean_key > second_clean_key:
            delta = intervals.measure(second_clean_key, first_clean_key)
            smaller = 'second'
        else:
            delta = intervals.measure(first_clean_key, second_clean_key)
            smaller = 'first'
    else:
        if min in song1.key:
            equiv_key, _ = find_equivalent_key_chord(first_clean_key, min)
        else:
            equiv_key, _ = find_equivalent_key_chord(second_clean_key, min)
        if first_clean_key > second_clean_key:
            delta = intervals.measure(equiv_key, second_clean_key)
            smaller = 'second'
        else:
            delta = intervals.measure(second_clean_key, equiv_key)
            smaller = 'first'

    if smaller == 'first':
        song1.data = librosa.effects.pitch_shift(song1.data, delta)
    else:
        song2.data = librosa.effects.pitch_shift(song2.data, delta)


def find_equivalent_key_chord(key: str, chord: SCALE_TYPE) -> (str, str):
    """
    key: 'C', 'A', 'F#', etc...
    chord: 'major' or 'minor'
    returns the equivalent key in the opposing chord
    """
    if key not in KEYS:
        raise Exception(f'{key} given as parameter is not an accepted key')

    if chord == SCALE_TYPE.major:
        rel_key = keys.relative_minor(key)
        rel_scale_type = SCALE_TYPE.minor
    else:
        rel_key = keys.relative_major(key)
        rel_scale_type = SCALE_TYPE.major
    return rel_key, rel_scale_type


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
    idx1 = random.randrange(len(bkps1) - 1)
    idx2 = random.randrange(len(bkps2) - 1)

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
            data2=data2[ms_to_frame(bkps2[idx2], sr2):ms_to_frame(bkps2[idx2 + 1], sr2)],
            sr2=sr2,
            start_ms=bkps1[idx1],
            inst=inst
        ) if no_change else overlay(
            data1=data2,
            sr1=sr2,
            data2=data1[ms_to_frame(bkps1[idx1], sr1):ms_to_frame(bkps1[idx1 + 1], sr1)],
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
    print(f'{sr} * {ts} // 1000 = {sr // 1000 * ts}')
    return sr // 1000 * ts


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
    max_curve = None

    for bkp_pos in range(1, len(bkps_costs) - 1):
        # given point b:(x_i,y_i), we will find the angle between a:(x_i-1,y_i-1) and c:(x-i+1,y_i+1)
        # going through point b
        curve = compute_curve(bkp_pos - 1, bkps_costs[bkp_pos - 1],
                              bkp_pos, bkps_costs[bkp_pos],
                              bkp_pos + 1, bkps_costs[bkp_pos + 1])
        if not max_curve:
            max_angle = curve
            continue
        if curve > max_curve:
            max_curve = curve
            max_pos = bkp_pos
            # print(f"max_pos: {max_pos}, max_angle: {max_angle}")
    return max_pos + 1


def compute_curve(x1, y1, x2, y2, x3, y3):
    first_decline = (y1 - y2) / (x1 - x2)
    second_decline = (y2 - y3) / (x2 - x3)
    return first_decline/second_decline


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
    voices = Separator("spleeter:5stems").separate(data)
    processed_voices = {n: to_mono(v) for n, v in voices.items()} if as_mono else voices
    return processed_voices


def get_clean_freq(data: np.ndarray):
    n = data.shape[-1]
    f = np.fft.fft(data, n)
    psd = f * np.conj(f) / n
    ind = psd > np.average(psd)
    return np.fft.ifft(ind * f)


def fig_ax(figsize=(15, 5), dpi=150):
    """Return a (matplotlib) figure and ax objects with given size."""
    return plt.subplots(figsize=figsize, dpi=dpi)


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

    n_bkps = 5
    # n_bkps = optimal_bkps(bkps_costs)
    print(f"n_bkps: {n_bkps}")

    # Segmentation
    bkps = algo.predict(n_bkps=n_bkps+1)   # HARD CODED ADDITION OF BKPS! Notice
    # Convert the estimated change points (frame counts) to actual timestamps
    bkps_times = librosa.frames_to_time(bkps, sr=samplerate, hop_length=hop_length)
    if in_ms:
        bkps_times *= 1000
        bkps_times = bkps_times.astype("int32")
    return bkps_times


def break_to_timed_segments(data: np.ndarray, sr: int, n_bkps_max: int = 10) -> np.ndarray:
    bkps = partition(data, sr, n_bkps_max, in_ms=True)
    print(f"bkps: {bkps}")
    i = 0
    rocks = np.empty([len(bkps) - 1], dtype=np.ndarray)
    #print('BREAKING IT DOWN:')
    for bkp1, bkp2 in zip(bkps[:-1], bkps[1:]):
        t1, t2 = ms_to_frame(bkp1, sr), ms_to_frame(bkp2, sr)
        #print(f'current t, t2 = {t1}, {t2}')
        rocks[i] = data[t1:t2]
        i += 1
    print(f'num of segments = {i}')
    return rocks, bkps


def slice_to_audio_layers(part: np.ndarray, sr: int) -> np.ndarray:
    layers = np.empty([5], dtype=np.ndarray)
    voices_as_mono = separate_voices(part)
    j = 0
    layers[0]
    for inst, data in voices_as_mono.items():
        layers[j] = data, sr
        j += 1
    return layers


def to_mingus_form(note: str):
    '''
    converts xi to x-i. for example: A8 -> A-8, B#4 -> B#-4
    '''
    if note is None:
        return None
    elif '-' in note:
        if '1' in note:
            note = re.sub(r'([^A-Z0-9\-])', '#', note)
            note_split = str.split(note, '-')
            return Note(note_split[0], -1)
        else:
            return None
    else:
        return Note(re.sub(r'([^0-9])([0-9])', r'\1-\2', re.sub(r'([^A-Z0-9])', '#', note)))


def calc_win_length_by_beat_track(bit_track: np.ndarray):
    bit_track = librosa.frames_to_samples(bit_track)
    beat_track_len = bit_track.shape[0]
    first_space = bit_track[2] - bit_track[1]
    mid_space = bit_track[round((beat_track_len/3)+1)] - \
                bit_track[round(beat_track_len/3)]
    last_space = bit_track[round((2*beat_track_len/3)+1)] - \
                 bit_track[round(2*beat_track_len/3)]
    return round((first_space + mid_space + last_space)/3)


def to_librosa_key(key:str):
    key = re.sub(r'\s+', r':', key)
    return key.replace('minor', 'min').replace('major', 'maj')


def extract_notes(data: np.ndarray, corresponding_beat_drops: np.ndarray, sr: int=22050):
    logger = log()
    # we want stft windows numbered as bit frames
    win_length = calc_win_length_by_beat_track(corresponding_beat_drops)
    logger.info(f'calculated win_length of {win_length}')
    corr_frequencies = librosa.fft_frequencies(sr=sr, n_fft=win_length)
    #logger.info(f'corresponding frequencies: {corr_frequencies}')
    freq_domain = librosa.stft(data, n_fft=win_length, hop_length=round(win_length))
    freqs_list = np.empty([freq_domain.shape[0]], dtype=np.ndarray)
    notes_list = np.empty([freq_domain.shape[0]], dtype=np.ndarray)
    #chords_list = np.empty([freq_domain.shape[0]], dtype=object)
    j = 0
    try:
        for beat_frame_freqs in freq_domain:
            i = 0
            idx_keeper = 0
            #logger.info('filtering out non-dominant frequencies...')
            min_freq = 4 * (np.max(beat_frame_freqs)) / 5
            only_true_idxs = np.where(beat_frame_freqs >= min_freq)
            freqs_list[j] = np.empty([len(only_true_idxs[0])], dtype=np.float32)
            for idx in only_true_idxs[0]:
                #logger.info('transcribing index to frequency..')
                freqs_list[j][i] = corr_frequencies[idx]
                i += 1
                idx_keeper = idx
            notes_list[j] = librosa.hz_to_note(freqs_list[j]) if 0 not in only_true_idxs[0] else None
            #logger.info(f'current notes: {notes_list[j]}')
            j += 1
    except Exception as e:
        logger.error(f'FELL ON (black days...): i = {i-1}, j = {j-1}, idx = {idx_keeper}, value = {corr_frequencies[idx_keeper]}\nError: {e.__str__()}')
        exit(1)
    return notes_list, win_length
    # get the chord according to the frequencies in each


def extract_key(data: np.ndarray, sr: int):
    # Use naive Bayes classifier to guess the key of SongInGMajor.mp3
    naive_bayes = classifiers.NaiveBayes()
    dist = pd.PitchDistribution.pitch_distribution(data, sr)
    key = naive_bayes.get_key(dist)

    # Use Krumhansl-Schmuckler classifier to guess the key of SongInBMinor.mp3
    krumhansl_schmuckler = classifiers.KrumhanslSchmuckler()
    dist = pd.PitchDistribution.pitch_distribution(data, sr)
    #key = krumhansl_schmuckler.get_key(dist)
    return key


def compute_similarity_matrix_slow(self, chroma):
    """Slow but straightforward way to compute time time similarity matrix"""
    num_samples = chroma.shape[1]
    time_time_similarity = np.zeros((num_samples, num_samples))
    for i in range(num_samples):
        for j in range(num_samples):
            # For every pair of samples, check similarity
            time_time_similarity[i, j] = 1 - (
                np.linalg.norm(chroma[:, i] - chroma[:, j]) / sqrt(12))

    return time_time_similarity
#
# def idx_2_freq(i: int, sr: float, n_fft: int):
#     return float(i * (sr / n_fft / 2.))
