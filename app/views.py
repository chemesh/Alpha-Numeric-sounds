from django.shortcuts import render
from django.contrib.auth.models import UserManager
from secrets import token_urlsafe

from django.http import HttpResponse, HttpRequest

N_BYTES = 32

manager = UserManager()

def index(request: HttpRequest):

    return HttpResponse("Hello, world. You're at the Alpha Numeric Sounds index.")

def get_token(request):
    token = token_urlsafe(N_BYTES)
    manager.create_user()


def add_songs_from_url(request):
