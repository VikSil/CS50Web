from django.contrib import admin
from .models import *

# Register your models here.

class AuctionAdmin(admin.ModelAdmin):
    list_display = ("id", "active", "CategoryID", "UserID", "title", "description", "imageURL")

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "IsStarting", "UserID", "amount", "AuctionID", "when",)

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "UserID", "AuctionID", "text", "when")

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

class UserAdmin(admin.ModelAdmin):
    list_display = ("username","first_name", "last_name", "email", "is_active", "is_superuser") 

admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User,UserAdmin)
