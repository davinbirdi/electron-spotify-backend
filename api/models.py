from django.db import models
from django.contrib.auth.models import User


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner')
    email = models.EmailField(max_length=150, null=True)
    spotify_id = models.CharField(max_length=900, default='')
    access_token = models.CharField(max_length=900, default='')

    def __str__(self):
        return self.user.username

