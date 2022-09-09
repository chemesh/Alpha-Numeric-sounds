import json
import os

from rest_framework.decorators import api_view
from django.http import HttpResponse, HttpRequest
from Source.scripts.alpha import start
from app.integrations.youtube_manager import YTManager
from app.app_utils import csv_to_list, STATUS, BasicContent
from .models import Execution


def run_algo(urls, params):
    # fetch songs data from youtube
    yt_manager = YTManager()
    songs_paths = yt_manager.download(urls)

    # call the backend logic
    out_path = start(songs_paths)

    # return algorithm results
    mapped_data = {}
    for idx, file in enumerate(os.listdir(out_path)):
        with open(file, 'rb') as f:
            mapped_data[str(idx)] = f.read()

    return mapped_data

def index(request):
    return HttpResponse("Hello, world. You're at the Alpha Numeric Sounds index.")

@api_view(['POST'])
def add_songs_from_url(request: HttpRequest):
    """
    Request format:
    {
        "urls"(list): "[url1,url2]"
        "advanced"(json):   {
                                "max_gens": int,
                                "population_size": int,
                                "selection_p": int(0-100),
                                "mutation_prob": int(0-100),
                                "crossover_prob": int(0-100)
                            }
    }
    """
    class Content(BasicContent):
        msg = ""
        error = ""

    response = HttpResponse(content_type="application/json")
    content = Content()
    try:
        urls = csv_to_list(request.GET['urls'])
        ea_params = json.loads(request.GET['advanced'])


        response.status_code = 200
        content.msg = "ok. starting to download urls"
    except Exception as e:
        response.status_code = 401
        content.msg = "could not verify parameters"
        content.error = e

    response.write(content.as_json())
    return response


@api_view(['GET'])
def poll_updates(request):
    """
    Request format: {}
    """
    class Content(BasicContent):
        status = ""
        percentage = None
        error = ""

    response = HttpResponse(content_type="application/json")
    content = Content()
    try:

        # TODO: insert polling logic here

        response.status_code = 200
        content.status = STATUS.IN_PROGRESS
        content.percentage = 60

    except Exception as e:
        response.status_code = 401
        content.status = STATUS.ERROR
        content.percentage = -1
        content.error = e

    response.write(content.as_json())
    return response






