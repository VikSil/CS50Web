from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("following", views.following, name="following"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile=<str:user_name>", views.profile, name="profile"),
    path("edit", views.edit_post, name="edit"),
    path("like", views.like_post, name="like"),
]
