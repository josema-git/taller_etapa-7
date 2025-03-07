from django.contrib.auth.models import User, Group
from django.db import models

# Create your models here.
    
class Blogger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.CharField(max_length=25, default='team_default')

    def __str__(self):
        return self.user.username