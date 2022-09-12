import librosa
import numpy as np
import server.Source.utils.SoundUtils as su


class Song(object):

    def __init__(self, data: np.ndarray, sr: int = 22050):
        self._data, _ = librosa.effects.trim(data)
        self.sr = sr
        self._tempo = None
        self._beat_frames = None
        self._segments_time_bkps = None
        self._key = None

    def _get_tempobeat(self):
        self._tempo, self._beat_frames = librosa.beat.beat_track(y=self._data, sr=self.sr)

    def _get_bkps(self):
        max_bkps = su.get_max_bkps(self.tempo, librosa.get_duration(self._data, self.sr))
        print(f"max bkps: {max_bkps}")
        self._segments_time_bkps = su.partition(self._data, self.sr, max_bkps, in_ms=True)
        print(f"segments timestamps: {self._segments_time_bkps}")

    def to_librosa_model(self):
        pass

    def to_paa_model(self):
        pass

    def _get_key(self):
        self._key = su.extract_key(self._data, self.sr)

    @property
    def data(self):
        return self._data

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

    @property
    def segments_time_bkps(self):
        if self._segments_time_bkps is None:
            self._get_bkps()
        return self._segments_time_bkps

    @property
    def key(self) -> str:
        if not self._key:
            self._get_key()
        return self._key

    @tempo.setter
    def tempo(self, value):
        self._tempo = value
        return

    @data.setter
    def data(self, value):
        self._data = value
        return

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
        return su.rand_reconstruct(self._pool[0].data, self._pool[0].sr,
                                   self._pool[1].data, self._pool[0].sr,
                                   bkps1=self._pool[0].segments_time_bkps,
                                   bkps2=self._pool[1].segments_time_bkps)[0]

    def get(self, index):
        return self._pool[index].data


class EmptyPoolException(Exception):
    pass

