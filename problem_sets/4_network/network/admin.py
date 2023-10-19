from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.


class PostAdmin(admin.ModelAdmin):
    list_display = ("UserID", "message", "timestamp", "get_likes")


class FollowingAdmin(admin.ModelAdmin):
    list_display = ("CreatorID", "FollowerID")


admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Following, FollowingAdmin)
