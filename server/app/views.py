import json
import uuid
from base64 import b64encode

from datetime import datetime
from django.db import transaction, connections
from rest_framework.decorators import api_view
from django.http import HttpResponse, HttpRequest
from app.app_utils import csv_to_list, STATUS, BasicContent
from .models import Execution
from controller.Controller import Controller
from django.views.decorators.csrf import csrf_exempt
from app.service import create_content_from_result

controller = Controller()


def index(request):
    # TODO: here we need to return the UI main page
    return HttpResponse("Hello, world. You're at the Alpha Numeric Sounds index.")


@csrf_exempt
@transaction.non_atomic_requests
@api_view(['POST'])
def add_songs_from_url(request: HttpRequest):
    """
    URL: https://[ip]:[port]/addSongsFromUrl
    -------------------------------------------
    Request format:
    {
        "urls": "[url1, url2]"
        "advanced": {
                        "max_gens": int,
                        "population_size": int,
                        "selection_p": int(0-100),
                        "mutation_prob": int(0-100),
                        "crossover_prob": int(0-100)
                    }
    }
    -------------------------------------------
    Response ex:
    {
        "msg": "ok. starting to fetch audio data from urls",
        "error": "",
        "id": "c692a9cd-b2d3-4574-ba2d-a042bbfc2c08"
    }

    """
    class Content(BasicContent):
        def __init__(self):
            self.msg = ""
            self.error = ""
            self.id = None

    response = HttpResponse(content_type="application/json")
    content = Content()
    try:
        # urls = csv_to_list(request.GET['urls'])
        data = json.loads(request.body)
        urls = data['urls']
        ea_params = data['advanced']
        execution = Execution(identifier=uuid.uuid4(), timestamp=datetime.now(), state=STATUS.INIT)
        execution.save()
        content.id = str(execution.identifier)

        connections.close_all()
        controller.start_exec(urls, ea_params, content.id)

        response.status_code = 200
        content.msg = "ok. starting to fetch audio data from urls"
    except Exception as e:
        response.status_code = 404
        content.msg = "could not verify parameters"
        content.error = str(e)

    response.write(content.as_json())
    return response


@api_view(['GET'])
def poll_updates(request, exec_id):
    """
    Request format: {}
    """
    class Content(BasicContent):
        def __init__(self):
            self.id = ""
            self.status = ""
            self.isReady = False
            self.file64 = ""
            self.error = ""

    response = HttpResponse(content_type="application/json")
    response.status_code = 200
    content = Content()
    try:
        # get data on execution with exec_id from DB
        exec_model = Execution.objects.get(identifier=exec_id)
        content.id = exec_model.identifier
        content.status = exec_model.state

        if exec_model.state == STATUS.DONE:
            # return the response with encoded file
            with exec_model.result.open("rb")as f:
                content.file64 = str(b64encode(f.read()).decode('utf-8'))
            content.isReady = True
            exec_model.delete()

    except Exception as e:
        response.status_code = 404
        content.status = STATUS.ERROR
        content.error = e
        content.isReady = False
        if content.file64:
            content.file64 = ""

    response.write(content.as_json())
    return response






