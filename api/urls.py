from django.contrib import admin
from django.urls import path, include
from .views import register_user, login_user, add_code, setup_success, get_playlists, get_songs_by_playlist,\
    choose_songs_to_rate, get_profile, play, pause

urlpatterns = [
    path('register', register_user),
    path('login', login_user),
    path('add-code', add_code),
    path('setup-success', setup_success),
    path('get-playlists', get_playlists),
    path('get-songs-by-playlist', get_songs_by_playlist),
    path('choose-songs-to-rate', choose_songs_to_rate),
    path('get-profile', get_profile),
    path('play', play),
    path('pause', pause),
    path('get-song', play)
]
