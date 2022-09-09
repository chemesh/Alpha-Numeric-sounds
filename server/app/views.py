import json
import os

from rest_framework.decorators import api_view
from django.http import HttpResponse, HttpRequest
from Source.scripts.alpha import start
from app.integrations.youtube_manager import YTManager
from app.app_utils import csv_to_list


def index(request: HttpRequest):
    return HttpResponse("Hello, world. You're at the Alpha Numeric Sounds index.")

@api_view(['GET'])
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
    urls = csv_to_list(request.GET['urls'])
    ea_params = json.loads(request.GET['advanced'])
    # fetch songs data from youtube
    yt_manager = YTManager()
    songs_paths = yt_manager.download(urls)

    # call the backend logic
    out_path = start(songs_paths)

    # return algorithm results
    mapped_data = {}
    content_size = 0
    for idx, file in enumerate(os.listdir(out_path)):
        with open(file, 'rb') as f:
            mapped_data[str(idx)] = f.read()
            content_size += os.path.getsize(file)

    response = HttpResponse()
    response.write(json.dumps(mapped_data))
    response['Conte Type'] ='audio/wav'
    response['Content-Length'] = content_size
    return response




