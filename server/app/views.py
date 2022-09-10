import json
import os

from datetime import datetime
from rest_framework.decorators import api_view
from django.http import HttpResponse, HttpRequest
from Source.scripts.alpha import start
from app.integrations.youtube_manager import YTManager
from app.app_utils import csv_to_list, STATUS, BasicContent
from .models import Execution
import uuid


def run_algo(urls, params, execution_model: Execution):
    # fetch songs data from youtube
    yt_manager = YTManager()
    songs_paths = yt_manager.download(urls)

    # update songs localpath in DB
    execution_model.song_1 = songs_paths[0]
    execution_model.song_2 = songs_paths[1]
    execution_model.state = STATUS.IN_PROGRESS
    execution_model.save()

    # call the backend logic
    out_path = start(songs_paths)

    # save the algorithm results to DB
    execution_model.result = out_path
    execution_model.state = STATUS.DONE
    execution_model.save()


def index(request):
    # TODO: here we need to return the UI main page
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
        id = None

    response = HttpResponse(content_type="application/json")
    content = Content()
    try:
        # urls = csv_to_list(request.GET['urls'])
        urls = json.loads(request.GET['urls'])
        ea_params = json.loads(request.GET['advanced'])
        execution = Execution(identifier=uuid.uuid4(), timestamp=datetime.now(), state=STATUS.INIT)
        execution.save()
        content.id = execution.identifier

        # TODO: add context manager logic to execute run_algo() asynchronously

        response.status_code = 200
        content.msg = "ok. starting to fetch audio data from urls"
    except Exception as e:
        response.status_code = 404
        content.msg = "could not verify parameters"
        content.error = e

    response.write(content.as_json())
    return response


@api_view(['GET'])
def poll_updates(request, exec_id):
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
        response.status_code = 404
        content.status = STATUS.ERROR
        content.percentage = -1
        content.error = e

    response.write(content.as_json())
    return response






