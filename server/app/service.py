import sys

from Source.utils.Constants import OUTPUT_FOLDER
from Source.utils.Logger import Logger
import base64

def create_content_from_result(exec_id):
    path = f'{sys.path[0]}/{OUTPUT_FOLDER}/result_{exec_id}'
    try:
       return base64.b64encode(open(f'{path}.wav', "rb").read()).decode('utf-8')
    except:
        Logger().error(f"file not found: {path}.wav")
        return -1