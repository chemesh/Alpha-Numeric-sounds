import os.path
import multiprocessing
import traceback
import soundfile as sf

from Source.utils.Logger import Logger
from Source.utils.Constants import OUTPUT_FOLDER
from Source.scripts.EA_Engine import EA_Engine
from Source.utils.DataModels import Song
from app.integrations.youtube_manager import YTManager
from app.app_utils import STATUS
import django
django.setup()
from app.models import Execution


class Controller:
    logger = Logger()
    engine = EA_Engine(logger)
    process_list = {}

    def start_exec(self, urls, params, exec_id):

        try:
            self.logger.info(f"creating process with execution {exec_id}")
            self.process_list[exec_id] = multiprocessing.Process(target=self._run, args=(urls, params, execution_model,))
            self.logger.info(f"start execution {exec_id}")
            self.process_list[exec_id].start()

        except Exception as e:
            msg = f"could not execute process {exec_id}! Error: {e}"
            self.logger.error(msg)
            raise ExecutionError(msg)

    def _run(self, urls, params, execution_model):
        try:
            # fetch songs data from youtube
            yt_manager = YTManager()
            songs_paths = yt_manager.download(urls)

            # update songs localpath in DB
            execution_model.song_1 = songs_paths[0]
            execution_model.song_2 = songs_paths[1]
            execution_model.state = STATUS.IN_PROGRESS
            execution_model.save()

            # Backend logic
            # songs = [Song.from_wav_file(path) for path in songs_paths]
            # results = self.engine.mix(*songs, **params)
            # file_path = os.path.join(OUTPUT_FOLDER, f"result_{execution_model.identifier}")
            # sf.write(f"{file_path}.wav", results[0].data, results[0].sr)

            # for testing only
            file_path = "C:\\Users\\roy12\\PycharmProjects\\AlphaNumericSounds\\server\\resources\\AD-FinalCountdown_pt2.wav"

            # save the algorithm results to DB
            execution_model.result = file_path
            execution_model.state = STATUS.DONE
            execution_model.save()

        except Exception as e:
            execution_model.state = STATUS.ERROR
            self.logger.error(e)
            self.logger.error(traceback.format_exc())


class ExecutionError(Exception):
    """
    Exception occurring in the start or during the execution of
    """