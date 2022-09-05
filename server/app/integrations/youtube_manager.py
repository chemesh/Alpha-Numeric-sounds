import os
import youtube_dl
import server.app.integrations.constants as consts

SONG_TEMPLATE_NAME = '%(title)s.%(ext)s'

YDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(os.path.abspath(consts.RESOURCE_DIR), SONG_TEMPLATE_NAME),
    'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '44',
        }]
}


class YTManager:

    def __init__(self):
        self._dpath = consts.RESOURCE_DIR
        self._download_descriptor = youtube_dl.YoutubeDL

    @property
    def dpath(self):
        return self._dpath

    def download(self, urls: list[str]):
        with self._download_descriptor(YDL_OPTS) as ydl:
            ydl.download(urls)
        return self._get_files()

    def _get_files(self):
        return [os.path.join(self._dpath, file) for file in os.listdir(self._dpath) if file.endswith('.wav')]





