from django.contrib import admin
from base.models import Task,Team,Profile,CustomUser
# Register your models here.

admin.site.register(Task)
admin.site.register(Team)
admin.site.register(Profile)
admin.site.register(CustomUser)