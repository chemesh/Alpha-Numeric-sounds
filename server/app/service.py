from Source.utils.Constants import OUTPUT_FOLDER
from os.path import exists
from app.app_utils import csv_to_list, STATUS, BasicContent
from Source.utils.Logger import Logger
import base64
import json

# __ERROR__: file not found: ../output/result_012.wav
def convert_track_to_base64(exec_id):
    path = "server/Source/output/result_012.wav"
    try:
        return base64.b64encode(open(path, "rb").read()).decode('utf-8')
    except:
        Logger().error(f"file not found: {path}")
        return -1


def create_content_from_result(exec_id, response):
    class Content(BasicContent):
        exec_id = ''
        is_ready = True
        file64 = ''
        msg = ''
        error = ''

    content = Content()
    try:
        base64res = convert_track_to_base64(exec_id)
        response.status_code = 200
        content.msg = "result is ready"
        content.exec_id = exec_id
        content.file64 = base64res
    except Exception as e:
        response.status_code = 401
        content.msg = "could not verify parameters"
        content.error = e
    Logger().info(f'content: {content}')
    return content
