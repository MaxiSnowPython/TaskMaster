from django.contrib import admin
from base.models import *
# Register your models here.

admin.site.register(Task)
admin.site.register(Team)
admin.site.register(CustomUser)
admin.site.register(Difficulty)