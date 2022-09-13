import multiprocessing
import os.path
import traceback

import django
import soundfile as sf
from Source.scripts.EA_Engine import EA_Engine
from Source.utils.Constants import OUTPUT_FOLDER
from Source.utils.DataModels import Song
from Source.utils.Logger import Logger
from app.app_utils import STATUS
from app.integrations.youtube_manager import YTManager
from controller.UIParser import UIParser

django.setup()
from app.models import Execution


class Controller:
    logger = Logger()
    engine = EA_Engine(logger)
    parser = UIParser()
    process_list = {}

    def start_exec(self, urls, params, exec_id):
        try:
            self.logger.info(f"creating process with execution {exec_id}")
            self.process_list[exec_id] = multiprocessing.Process(target=self._run, args=(urls, params, exec_id))
            self.logger.info(f"start execution {exec_id}")
            self.process_list[exec_id].start()

        except Exception as e:
            msg = f"could not execute process {exec_id}! Error: {e}"
            self.logger.error(msg)
            raise ExecutionError(msg)

    def _run(self, urls, params, exec_id):
        execution_model = Execution.objects.get(identifier=exec_id)
        try:
            # fetch songs data from youtube
            self.logger.info("starting to download songs audio data from yt...")
            yt_manager = YTManager()
            songs_paths = yt_manager.download(urls)
            self.logger.info("successfully downloaded audio data")

            # update songs localpath in DB
            execution_model.song_1 = songs_paths[0]
            execution_model.song_2 = songs_paths[1]
            execution_model.state = STATUS.IN_PROGRESS
            self.logger.info(f"execution {execution_model.identifier} status: {STATUS.IN_PROGRESS}")
            execution_model.save()
            self.logger.info(f"updated DB for execution {execution_model.identifier}:"
                             f"audio data saved in {execution_model.song_1}"
                             f"and {execution_model.song_2}")

            # Backend logic
            songs = [Song.from_wav_file(path, duration=30) for path in songs_paths]
            self.logger.info(f"params from ui: {params}")
            ea_params = self.parser.parse_ea_params(params)
            self.logger.info(f"params from ui: {ea_params.json()}")
            results = self.engine.mix(*songs, **ea_params.json())
            file_path = os.path.join(OUTPUT_FOLDER, f"result_{execution_model.identifier}")
            sf.write(f"{file_path}.wav", results.data, results.sr)

            # for testing only
            file_path = songs_paths[0]

            # save the algorithm results to DB
            execution_model.result = file_path
            execution_model.state = STATUS.DONE
            execution_model.save()

        except Exception as e:
            execution_model.state = STATUS.ERROR
            execution_model.save()
            self.logger.error(e)
            self.logger.error(traceback.format_exc())

        finally:
            exit(0)



class ExecutionError(Exception):
    """
    Exception occurring in the start or during the execution of
    """