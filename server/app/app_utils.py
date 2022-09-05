from typing import List


def csv_to_list(csv: str, delimiter=',') -> List:
    return csv.split(delimiter)