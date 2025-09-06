from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Team,Task,CustomUser

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
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
        fields = ('name', 'creator', 'members', 'created_at')

class TaskSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)  # для чтения
    team = TeamNameSer(read_only=True)         # для чтения
    team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(), write_only=True, source='team'
    )  # для создания/обновления через POST

    class Meta:
        model = Task
        fields = ('id', 'team', 'team_id', 'user', 'title', 'xp', 'complete', 'created')