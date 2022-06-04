import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple


class Pool(object):
    def __init__(self):
        self._pool = []
        self._pop_counter = 0

    def add(self, obj: Tuple[int, np.ndarray]):
        if obj not in self._pool:
            self._pool.append(obj)

    def pop(self) -> Tuple[int, np.ndarray]:
        index = self._pop_counter % len(self._pool)
        obj = self._pool[index]
        self._pop_counter += 1
        return obj


def fig_ax(figsize=(15, 5), dpi=150):
    """Return a (matplotlib) figure and ax objects with given size."""
    return plt.subplots(figsize=figsize, dpi=dpi)
