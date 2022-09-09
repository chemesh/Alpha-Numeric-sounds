import json
from abc import ABC
from enum import Enum
from typing import List


class STATUS:
    INIT = "fetching resources and configurations"
    IN_PROGRESS = "song mixing in progress..."
    DONE = "Mash-up is done!"
    ERROR = "An error occurred in the algorithm execution"


class BasicContent(ABC):
    """
    abstract class for basic http response content DTO
    """
    def __str__(self):
        return str(vars(self))

    def as_json(self):
        return json.dumps(vars(self))


def csv_to_list(csv: str, delimiter=',') -> List:
    return csv.split(delimiter)


