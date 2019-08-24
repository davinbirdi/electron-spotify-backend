from django.shortcuts import render
import requests
import spotipy
import spotipy.util as util
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponseRedirect

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

def get_playlists(request):
    user_id = request.GET['user_id']
    custom_user = CustomUser.objects.get(id=user_id)
    token = custom_user.access_token
    username = custom_user.spotify_id
    sp = spotipy.Spotify(auth=token)
    playlists = sp.user_playlists(username)
    playlist_list = [playlist for playlist in playlists['items']]
    print(playlist_list)
    return JsonResponse({'status': 200, 'playlists': playlist_list})
