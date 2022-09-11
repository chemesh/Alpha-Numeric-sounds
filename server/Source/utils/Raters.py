import librosa
import numpy as np
from mingus.containers import Note
import server.Source.utils.SoundUtils as su
import server.Source.utils.Logger as log

def sub_rater_neighboring_pitch(notes: np.ndarray, need_mingus_conversion:bool = True):
    """
    Calculates rating according to number of crazy notes
    Only relevant for list of notes, or list of lists with one note each.
    """
    # iterate through the array of notes
    notes = [x[0] for x in notes if x is not None]
    mingus_notes = list(map(su.to_mingus_form, notes)) if need_mingus_conversion else notes
    count_crazy_notes = 0
    for note1, note2 in zip(mingus_notes[:-1], mingus_notes[1:]):
        if note1 is not None and note2 is not None:
            if abs(note2.octave-note1.octave) >= 2:
                count_crazy_notes += 1
    print(f'counted {count_crazy_notes} crazy notes out of {len(mingus_notes)} notes a.i.a')
    #2DO think wether this should be (Ans) ot (1-Ans)
    return 1-count_crazy_notes/len(mingus_notes)

def sub_rater_notes_density_diversity(notes: np.ndarray):
    """
    Calculates rating according how rich is the segment
    """
    return

def sub_rater_notes_in_key(notes: np.ndarray, key):
    #2DO adjust the key to librosa representation of it
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
    return count_in_key/count_all_notes
