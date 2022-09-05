import os
import youtube_dl
import server.app.integrations.constants as consts

YDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': '{}/%(extractor)s-%(id)s-%(title)s.%(ext)s'.format(consts.RESOURCE_DIR)
}


class YTManager:

    def __init__(self):
        super(YTManager, self).__init__(YDL_OPTS)
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
        return [file for file in os.listdir(self._dpath) if file.endswith('.wav')]





