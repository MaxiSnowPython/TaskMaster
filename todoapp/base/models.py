from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Create your models here.



class CustomUser(AbstractUser):
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

class Task(models.Model):
    team = models.ForeignKey("Team", on_delete=models.CASCADE, null=True, blank=True, related_name="tasks")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="tasks")
    title = models.CharField(max_length=200, null=True, blank=True)
    xp = models.IntegerField(null=True)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['complete']

class Team(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name="created_teams")
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="teams")  
    name = models.CharField(max_length=100) 
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name
    
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True, blank=True, related_name="profile")
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='friends', blank=True)
    def __str__(self):
        return f"{self.user.username}"