from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Team,Task,Profile

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class TeamNameSer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name']


class TeamSerializer(serializers.ModelSerializer):
    members = UserMiniSerializer(many=True)
    creator = UserMiniSerializer()
    class Meta:
        model = Team
        fields = ('name','creator','members')

class TaskSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    team = TeamNameSer()
    class Meta:        
        model = Task
        fields = ('team','user','title','xp','complete','created')

class ProfileSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    friends = UserMiniSerializer(read_only=True,many = True)
    class Meta:
        model = Profile
        fields = ('user','friends')