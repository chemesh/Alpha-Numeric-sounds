import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple


def fig_ax(figsize=(15, 5), dpi=150):
    """Return a (matplotlib) figure and ax objects with given size."""
    return plt.subplots(figsize=figsize, dpi=dpi)


def is_converged(series):
    pass
