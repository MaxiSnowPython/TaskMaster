from django.contrib import admin
from base.models import Task,Team,Reward,UserProfile,Profile
# Register your models here.

admin.site.register(Task)
admin.site.register(Team)
admin.site.register(Reward)
admin.site.register(UserProfile)
admin.site.register(Profile)