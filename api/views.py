from django.shortcuts import render
import requests
import random
import spotipy
import spotipy.util as util
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from ast import literal_eval

CLIENT_ID = "baa5f3746bf74710bf3f6b18926993db"
SECRET_ID = "5617616ca51644b1b81eaf55efb56530"
REDIRECT_URI = "http://127.0.0.1:8000/setup-success"

@csrf_exempt
def register_user(request):
    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    custom_user = CustomUser(email=email, user=user)
    custom_user.save()
    theuser = authenticate(username=username, password=password)
    if theuser is not None:
        login(request, theuser)
        return JsonResponse({'status': 200, 'user_id': custom_user.id})
    else:
        return JsonResponse({'status': 400})


@csrf_exempt
def login_user(request):
    username = request.POST['username']
    password = request.POST['password']
    try:
        user = User.objects.get(username=username)
        custom_user = CustomUser.objects.get(user=user)
        theuser = authenticate(username=username, password=password)
        if theuser is not None:
            return JsonResponse({'status': 200, 'user_id': custom_user.id})
        else:
            return JsonResponse({'status': 400})
    except:
        return JsonResponse({'status': 400})


@csrf_exempt
def add_code(request):
    user_id = request.POST['user_id']
    custom_user = CustomUser.objects.get(id=user_id)
    code = request.POST['code']
    cred = spotipy.util.oauth2.SpotifyOAuth(CLIENT_ID, SECRET_ID, REDIRECT_URI)
    print("FIRST code : " + str(code))
    full_code = cred.get_access_token(code)
    print("full code : " + str(full_code))
    custom_user.access_token = full_code['access_token']
    sp = spotipy.Spotify(auth=full_code['access_token'])
    custom_user.spotify_id = sp.current_user()['id']
    custom_user.save()
    return JsonResponse({'status': 200, 'access_token': custom_user.access_token})


def setup_success(request):
    print("setup successful!")
    return HttpResponseRedirect('/api/add-code')

def get_profile(request):
    user_id = request.GET['user_id']
    custom_user = CustomUser.objects.get(id=user_id)
    token = custom_user.access_token
    sp = spotipy.Spotify(auth=token)
    name = sp.current_user()['display_name']
    pic = sp.current_user()['images'][0]['url']
    print(pic)
    return JsonResponse({'status': 200, 'name': name, 'pic': pic})

def get_playlists(request):
    user_id = request.GET['user_id']
    custom_user = CustomUser.objects.get(id=user_id)
    token = custom_user.access_token
    username = custom_user.spotify_id
    sp = spotipy.Spotify(auth=token)
    playlists = sp.user_playlists(username)
    playlist_list = [playlist for playlist in playlists['items']]
    return JsonResponse({'status': 200, 'playlists': playlist_list})

def get_songs_by_playlist(request):
    user_id = request.GET['user_id']
    playlist_id = request.GET['playlist_id']
    custom_user = CustomUser.objects.get(id=user_id)
    token = custom_user.access_token
    username = custom_user.spotify_id
    sp = spotipy.Spotify(auth=token)
    playlist_tracks_list = sp.user_playlist_tracks(user_id, playlist_id)
    playlist_tracks = [track for track in playlist_tracks_list['items']]
    return JsonResponse({'status': 200, 'playlist_tracks': playlist_tracks})

def choose_songs_to_rate(request):
    user_id = request.GET.get('user_id', '')
    custom_user = CustomUser.objects.get(id=user_id)
    token = custom_user.access_token
    username = custom_user.spotify_id
    sp = spotipy.Spotify(auth=token)
    user_playlists = sp.user_playlists(username)
    playlist_ids = request.GET.get('playlist_ids', [])
    playlist_ids = literal_eval(playlist_ids)
    playlist_ids = playlist_ids["songs"]
    print(playlist_ids)
    playlist_list = [playlist for playlist in user_playlists['items']]
    # playlist_name = request.GET['playlist-name']
    number_songs = request.GET.get('number_songs', '')
    selected_playlists = []
    for p in playlist_list:
        if p['id'] in playlist_ids:
            print(p['id'])
            selected_playlists.append(p)
    playlist_tracks_list = [sp.user_playlist_tracks(user_id, playlist_id) for playlist_id in playlist_ids]
    songs_by_playlist = [[song for song in p_list['items']] for p_list in playlist_tracks_list]
    rand_songs_by_playlist = [random.sample(songs, int(number_songs)) for songs in songs_by_playlist]
    print(rand_songs_by_playlist)
    return JsonResponse({'status': 200, 'playlists': selected_playlists, 'playlist_tracks': rand_songs_by_playlist})

def play(request):
    user_id = request.GET['user_id']
    track = request.GET['track_uri']
    device_id = request.GET['device_id']
    track_list = [track]
    print("DEVICE " + device_id)
    # track = 'spotify:track:' + track
    custom_user = CustomUser.objects.get(id=user_id)
    token = custom_user.access_token
    username = custom_user.spotify_id
    sp = spotipy.Spotify(auth=token)
    # sp.start_playback(device_id, uris = [track])
    return JsonResponse({'status': 200})

def pause(request):
    user_id = request.GET['user_id']
    custom_user = CustomUser.objects.get(id=user_id)
    token = custom_user.access_token
    sp = spotipy.Spotify(auth=token)
    sp.pause_playback(device_id = CLIENT_ID)
    return JsonResponse({'status': 200})

def get_token(request):
    user_id = request.GET['user_id']
    custom_user = CustomUser.objects.get(id=user_id)
    token = custom_user.access_token
    print(token)
    return JsonResponse({'status': 200, 'token': token})