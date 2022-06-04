from typing import Tuple

import numpy as np


class Song(object):
    def __init__(self, data, sr):
        self.sr = sr
        self.data = data

    def to_librosa_model(self):
        pass

    def to_paa_model(self):
        pass


class SongPool(object):
    def __init__(self):
        self._pool = []
        self._pop_counter = 0

    def add(self, obj: Song):
        if obj not in self._pool:
            self._pool.append(obj)

    def pop(self) -> Song:
        index = self._pop_counter % len(self._pool)
        obj = self._pool[index]
        self._pop_counter += 1
        return obj

