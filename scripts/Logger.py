from pathlib import Path
from datetime import datetime
import sys

LOG_FOLDER_PATH = "../logs"
LOG_FILENAME_FORMAT = "%Y/%m/%d,%h"


class Logger(object):
    def __init__(self):
        self._logs_folder = Path(LOG_FOLDER_PATH)
        self._logs_folder.mkdir(parents=True, exist_ok=True)

    def _record(self, msg, timestamp):
        file = self._get_path(timestamp)
        with file.open(mode="a") as f:
            f.write(msg+"\n")

    def _get_path(self, timestamp: datetime) -> Path:
        """
        returns the path for the log file correlated to timestamp
        :param timestamp: datetime object
        :return: pathlib.Path object
        """
        date, h = timestamp.strftime(LOG_FILENAME_FORMAT).split(",")
        path = self._logs_folder/date
        path.mkdir(parents=True, exist_ok=True)

        path = path/f"{h}.log"
        path.touch(exist_ok=True)
        return path

    def _log(self, log_type, msg, record=True, output=sys.stdout):
        time = datetime.now()
        log = f"{time}_{log_type}_: {msg}"
        print(log, file=output)
        if record:
            self._record(log, time)

    def debug(self, msg, record=True):
        self._log(
            log_type="DEBUG",
            msg=msg,
            record=record)

    def info(self, msg):
        self._log(
            log_type="INFO",
            msg=msg)

    def warn(self, msg):
        self._log(
            log_type="WARNING",
            msg=msg,
            output=sys.stderr)

    def error(self, msg):
        self._log(
            log_type="ERROR",
            msg=msg,
            output=sys.stderr)

