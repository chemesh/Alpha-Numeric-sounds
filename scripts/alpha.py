from deap import base, creator, tools
from pyAudioAnalysis import audioBasicIO, audioSegmentation, audioVisualization
import mingus

from constants import WAV_FILE_TEST


def main():
    samplerate, data = audioBasicIO.read_audio_file(WAV_FILE_TEST)
    print(f"sample rate: {samplerate}, data: {data}")

if __name__ == "__main__":
    main()
