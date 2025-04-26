from django.contrib.auth.models import User
import rest_framework
from rest_framework import serializers
from .models import Team

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']


class TeamSerializer(serializers.ModelSerializer):
    members = UserMiniSerializer(many=True)
    creator = UserMiniSerializer()

    class Meta:
        model = Team
        fields = ('name','creator','members')