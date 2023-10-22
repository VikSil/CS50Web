import json
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse

from .models import *


def index(request):
    """
    Displays All Posts page
    Takes a new post and saves it to the DB
    """
    # if POST, then save the new post for the current user
    if request.method == "POST":
        new_post = Post()
        new_post.UserID = User.objects.get(id=request.user.id)
        new_post.message = request.POST.get("post-message")
        new_post.save()

    # Get all posts in reverse order
    all_posts = Post.objects.all().order_by("-id")
    # Create paginator
    p = Paginator(all_posts, 10)
    # By default return first page, or another is user asked for another
    page = 1
    if request.GET.get("page"):
        page = request.GET.get("page")

    # Return data to display on All Posts page
    return render(
        request,
        "network/index.html",
        {"newpost": True, "profile": False, "posts": p.page(page)},
    )


@login_required
def following(request):
    """
    Displays posts from all users that the current user follows
    Only works for authorised users
    """
    # Fetch all the users whom current user follows
    following = Following.objects.filter(FollowerID=request.user.id).values_list(
        "CreatorID_id"
    )
    # Fetch all posts by those users in descending order
    followed_posts = Post.objects.filter(UserID__in=following).order_by("-id")
    # Create a paginator
    p = Paginator(followed_posts, 10)
    # By default return first page, or another is user asked for another
    page = 1
    if request.GET.get("page"):
        page = request.GET.get("page")

    # Return data to display on Following page
    return render(
        request,
        "network/index.html",
        {"newpost": False, "profile": False, "posts": p.page(page)},
    )


def edit_post(request):
    """
    Takes data from an edited post and saves it to the DB
    """
    # Can only be accessed by PUT, otherwise does nothing
    if request.method == "PUT":
        # Get current user
        user = User.objects.get(id=request.user.id)
        # Get the new message from PUT
        data = json.loads(request.body)
        # Get the post to be edited
        post = Post.objects.get(pk=data["postID"])

        # Check that the user that sent PUT is the user who made the post
        if post.UserID == user:
            # Amend post and save
            post.message = data["message"]
            post.save(update_fields=["message"])
        return HttpResponse(status=204)


def like_post(request):
    """
    Takes data from post (un)like and saves it to the DB
    """
    # Can only be accessed by PUT, otherwise does nothing
    if request.method == "PUT":
        # Get current user
        user = User.objects.get(id=request.user.id)
        # Get the like data from PUT
        data = json.loads(request.body)
        like = data["like"]
        # Get the post to be edited
        post = Post.objects.get(pk=data["postID"])

        # Add or remove the like
        if like:
            post.likedby.add(user)
        else:
            post.likedby.remove(user)
        return HttpResponse(status=204)


def profile(request, user_name):
    """
    Displays user profile and allows to (un)follow them
    """
    # Get the current user object from the DB
    user_id = User.objects.filter(username=user_name).first().id
    # will resolve to 1 if current user follows the profile they are viewing
    follow_flag = Following.objects.filter(
        FollowerID=request.user.id, CreatorID=user_id
    ).count()

    # If current user requested to (un)follow the profile user
    if request.method == "PUT":
        data = json.loads(request.body)
        # If follow request and current user does not follow the profile already
        if data["follow"] and not follow_flag:
            # Add a new follower and save to DB
            new_follower = Following()
            new_follower.CreatorID = User.objects.get(id=user_id)
            new_follower.FollowerID = User.objects.get(id=request.user.id)
            new_follower.save()
        # If unfollow request and user does follow the profile
        elif not data["follow"] and follow_flag:
            # Get the follower and delete from the DB
            follower = Following.objects.filter(
                FollowerID=request.user.id, CreatorID=user_id
            )
            follower.delete()
        # if request and follow flag gets out of syns - do nothing
        else:
            print("This should not be possible, need to debug")

        return HttpResponse(status=204)

    # If current user opened Profile page
    else:
        # Get number of following/followers
        followers = Following.objects.filter(CreatorID=user_id).count()
        following = Following.objects.filter(FollowerID=user_id).count()
        # Get profile user's posts in descending order
        users_posts = Post.objects.filter(UserID=user_id).order_by("-id")
        # Create a paginator
        p = Paginator(users_posts, 10)
        # By default return first page, or another is user asked for another
        page = 1
        if request.GET.get("page"):
            page = request.GET.get("page")

        # Pass Follow/Unfollow button text
        button_text = "Follow"
        if request.user.id and follow_flag:
            button_text = "Unfollow"

        # Return data to display on Profile page
        return render(
            request,
            "network/index.html",
            {
                "newpost": False,
                "profile": True,
                "posts": p.page(page),
                "username": user_name,
                "followers": followers,
                "following": following,
                "button": button_text,
            },
        )


# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
