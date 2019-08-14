from django.contrib import admin
from django.urls import path, include
from .views import register_user, login_user, add_code, setup_success

urlpatterns = [
    path('register', register_user),
    path('login', login_user),
    path('add-code', add_code),
    path('setup-success', setup_success),
]
