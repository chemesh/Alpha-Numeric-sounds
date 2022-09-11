from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('addSongsFromUrl', views.add_songs_from_url, name='add_songs_from_url'),
    path('pollForUpdates/<str:exec_id>', views.poll_updates, name='poll_updates'),
]