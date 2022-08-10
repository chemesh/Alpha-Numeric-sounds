from typing import overload, Iterable

import librosa
import numpy as np
from pydub import AudioSegment
import utils.SoundUtils as su


class Song(object):

    def __init__(self, data: np.ndarray, sr: int = 22050):
        self.data = data
        self.sr = sr
        self._tempo = None
        self._beat_frames = None

    def _get_tempobeat(self):
        self._tempo, self._beat_frames = librosa.beat.beat_track(y=self.data, sr=self.sr)

    def to_librosa_model(self):
        pass

    def to_paa_model(self):
        pass

    @property
    def tempo(self):
        if not self._tempo:
            self._get_tempobeat()
        return self._tempo

    @property
    def beat_frames(self):
        if not self._beat_frames:
            self._get_tempobeat()
        return self.beat_frames

    @property
    def beat_times(self):
        return librosa.frames_to_time(self.beat_frames, sr=self.sr)

    @staticmethod
    def from_wav_file(path: str, sr: int = 22050, duration: float = None):
        y, sr = librosa.load(path, sr=sr, duration=duration)
        return Song(y, sr)


class SongPool(object):

    def __init__(self):
        self._pool = []
        self._pop_counter = 0

    def add(self, *songs: Song):
        for s in songs:
            if s not in self._pool:
                self._pool.append(s)

    def pop(self) -> Song:
        index = self._pop_counter % len(self._pool)
        obj = self._pool[index]
        self._pop_counter += 1
        return obj

    def empty(self):
        self._pool.clear()
        self._pop_counter = 0

    def generate(self):
        if len(self._pool) < 2:
            raise EmptyPoolException
        return su.rand_reconstruct(self._pool[0].data, self._pool[0].sr, self._pool[1].data, self._pool[0].sr)


class EmptyPoolException(Exception):
    pass

