import librosa
import librosa.display
import soundfile as sf
import matplotlib.pyplot as plt
import numpy as np
from spleeter.separator import Separator
from pydub import AudioSegment
import mingus.core.notes
from mingus.containers import Note

from utils.Logger import Logger
from utils.Constants import WAV_FILE_TEST, INPUT_FOLDER
from scripts.EA_Engine import EA_Engine
from utils.DataModels import Song
import utils.SoundUtils as su

def sub_rater_neighbooring_pitch(notes: np.ndarray):
    '''
    Calculates rating according to number of crazy notes
    '''
    # iterate through the array of notes
    mingus_notes = map(su.to_mingus_form, notes)
    mingus_notes = list(map(Note, mingus_notes))
    print(mingus_notes)
    count_crazy_notes = 0
    for index, note in enumerate(mingus_notes):
        if index <= len(mingus_notes) and index - 1 > 0:
            next_el = mingus_notes[index+1]
            print(f'octave D:{next_el.octave-note.octave}')
            if abs(next_el.octave-note.octave) > 2:
                count_crazy_notes += 1
    print(f'counted {count_crazy_notes} crazy notes out of {len(mingus_notes)} notes a.i.a')
    return count_crazy_notes/len(mingus_notes)
    # for each two notes, calculate the distance in octaves
    # increase crazy note counter for each calculated distance beyond 2
    # return crazynotes counter divided by total number of notes

def sub_rater_notes_density_diversity(notes: np.ndarray):
    '''
    Calculates rating according how rich is the segment
    '''
    # iterate through the array of notes
    # for each two notes, calculate the distance in octaves
    # increase crazy note counter for each calculated distance beyond 2
    # return crazynotes counter divided by total number of notes
    return
