from django.db import models
from django.contrib.auth.models import AbstractUser, Group

# Create your models here.
class User(AbstractUser):
    group = models.ForeignKey(Group, on_delete=models.SET_DEFAULT, default='default_team' , related_name='users')