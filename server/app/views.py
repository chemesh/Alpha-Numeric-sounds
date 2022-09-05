import json
import os

from rest_framework.decorators import api_view
from django.http import HttpResponse, HttpRequest
from server.Source.scripts.alpha import start
from server.app.integrations.youtube_manager import YTManager


def index(request: HttpRequest):
    return HttpResponse("Hello, world. You're at the Alpha Numeric Sounds index.")


@api_view(['GET'])
def add_songs_from_url(request: HttpRequest):
    urls = request.POST['urls']
    ea_params = request.POST['advanced']
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
    response['Content-Type'] ='audio/wav'
    response['Content-Length'] = content_size
    return response




