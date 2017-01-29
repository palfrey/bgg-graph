from django.contrib import admin
from models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id',)