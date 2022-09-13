from typing import List
import math
import librosa
import numpy as np
from mingus.containers import Note
import server.Source.utils.SoundUtils as su
import server.Source.utils.Logger as log


def sub_rater_neighboring_pitch(notes: np.ndarray, need_mingus_conversion:bool = True):
    logger = log.Logger()
    """
    Calculates rating according to number of crazy notes
    Only relevant for list of notes, or list of lists with one note each.
    """
    logger.info(f'NOTES in rater pitch: {notes}')
    notes = [x[0] for x in notes if x is not None]
    mingus_notes = list(map(su.to_mingus_form, notes)) if need_mingus_conversion else notes
    count_crazy_notes = 0
    for note1, note2 in zip(mingus_notes[:-1], mingus_notes[1:]):
        if note1 is not None and note2 is not None:
            if abs(note2.octave-note1.octave) >= 2:
                count_crazy_notes += 1
    logger.info(f'counted {count_crazy_notes} crazy notes out of {len(mingus_notes)} notes a.i.a')
    return (1-count_crazy_notes/len(mingus_notes))**2


def sub_rater_notes_in_key(notes: np.ndarray, key):
    logger = log.Logger()
    """
    notes: list of note lists with one note or more each
    key: the key to check the notes against
    """
    count_in_key = 0
    count_all_notes = 0
    for note in notes:
        if note is not None:
            note = [su.to_mingus_form(x) for x in note]
            key = su.to_librosa_key(key)
            key_notes = librosa.key_to_notes(key)
            if None not in note:
                count_all_notes += len(note)
                count_in_key += sum(1 for nt in note if nt.name in key_notes)
    logger.info(f'counted {count_in_key} note in key {key} out of {count_all_notes} notes a.i.e')
    return count_in_key/count_all_notes if count_all_notes>0 else 1

def sub_rater_quiet_notes(notes: np.ndarray):
    return sum(1 for note in notes if not None)/len(notes)


def sub_rater_verify_parts_length(bkps_list: List):
    """
    This sub rater compares and verifies that the lengths of the essential parts of the song,
    have similar lengths in order of magnitude
    """

    # calculate the duration for each part
    parts_duration = [bkps_list[i] - bkps_list[i-1] for i in range(1, len(bkps_list))]
    avg_duration = sum(parts_duration) / len(bkps_list)

    # here d is the sum of 'distances' of all the parts durations from the average duration
    d = sum([abs(avg_duration - part_duration) % avg_duration for part_duration in parts_duration])

    return 1 - d / (len(bkps_list) * avg_duration)
