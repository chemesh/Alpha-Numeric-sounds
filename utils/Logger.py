from pathlib import Path
from datetime import datetime
import sys

LOG_FOLDER_PATH = "../logs"
LOG_DIRECTORY_FORMAT = "%Y/%m/%d,%H"
LOG_FILENAME_FORMAT = "%Y%m%d_%H"


class LOG_TYPE(object):
    """
    Enum class for log type string identifiers
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Logger(object):
    """
    Logger class for logging.
    use example:
        logger = Logger()
        logger.info("this is a log")
    """
    def __init__(self):
        self._logs_folder = Path(LOG_FOLDER_PATH)

    def _record(self, msg: str, timestamp: datetime) -> None:
        """
        Record the log in a log file, determined by the timestamp
        :param msg: Log message
        :param timestamp:  datetime object
        """
        file = self._get_path(timestamp)
        with file.open(mode="a") as f:
            f.write(msg+"\n")

    def _get_path(self, timestamp: datetime) -> Path:
        """
        returns the path for the log file correlated to timestamp
        :param timestamp: datetime object
        :return: pathlib.Path object
        """
        date, h = timestamp.strftime(LOG_DIRECTORY_FORMAT).split(",")
        path = self._logs_folder/date
        path.mkdir(parents=True, exist_ok=True)

        file_name = f"{timestamp.strftime(LOG_FILENAME_FORMAT)}.log"
        path = path/file_name
        path.touch(exist_ok=True)
        return path

    def _log(self, log_type: str, msg: str, record=True, output=sys.stdout) -> None:
        """
        Writes log to output
        :param log_type: string identifier for log type (i.e. "INFO")
        :param msg: log message
        :param record: if true, record log in file
        :param output: where to write the log to (default is stdout)
        """
        time = datetime.now()
        log = f"[{time}] __{log_type}__: {msg}"
        print(log, file=output)
        if record:
            self._record(log, time)

    def debug(self, msg: str, record=True):
        """
        Write debug log.
        :param msg: log message
        :param record: if true, record log in file
        """
        self._log(
            log_type=LOG_TYPE.DEBUG,
            msg=msg,
            record=record)

    def info(self, msg: str):
        """
        Write informative log
        :param msg: log message
        """
        self._log(
            log_type=LOG_TYPE.INFO,
            msg=msg)

    def warn(self, msg: str):
        """
        Write warning log
        :param msg: log message
        """
        self._log(
            log_type=LOG_TYPE.WARNING,
            msg=msg,
            output=sys.stderr)

    def error(self, msg: str):
        """
        Write error log
        :param msg: log message
        """
        self._log(
            log_type=LOG_TYPE.ERROR,
            msg=msg,
            output=sys.stderr)

