from typing import overload, Iterable

import librosa
import numpy as np


class Song(object):
    def __init__(self, path: str):
        self.data, self.sr = librosa.load(path)
        self._tempo, self._beat_frames = librosa.beat.beat_track(y=self.data, sr=self.sr)

    def to_librosa_model(self):
        pass

    def to_paa_model(self):
        pass

    @property
    def tempo(self):
        return self._tempo

    @property
    def beat_frames(self):
        return self.beat_frames

    @property
    def beat_times(self):
        return librosa.frames_to_time(self._beat_frames, sr=self.sr)


class SongPool(object):
    def __init__(self):
        self._pool = []
        self._pop_counter = 0

    @overload
    def add(self, obj: Song):
        if obj not in self._pool:
            self._pool.append(obj)

    @overload
    def add(self, collection: Iterable[Song]):
        for obj in collection:
            self.add(obj)

    def pop(self) -> Song:
        index = self._pop_counter % len(self._pool)
        obj = self._pool[index]
        self._pop_counter += 1
        return obj

    def empty(self):
        self._pool.clear()
        self._pop_counter = 0

