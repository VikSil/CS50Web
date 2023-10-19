import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.core.paginator import Paginator


from .models import *


def index(request):
    all_posts = Post.objects.all().order_by("-id")
    p = Paginator(all_posts, 10)

    page = 1
    if request.GET.get("page"):
        page = request.GET.get("page")

    return render(
        request,
        "network/index.html",
        {"newpost": True, "profile": False, "posts": p.page(page)},
    )


@login_required
def following(request):
    # Fetch all the users whom current user follows
    following = Following.objects.filter(FollowerID=request.user.id).values_list(
        "CreatorID_id"
    )
    # Fetch all posts by those users and order by id descending
    followed_posts = Post.objects.filter(UserID__in=following).order_by("-id")
    p = Paginator(followed_posts, 10)

    page = 1
    if request.GET.get("page"):
        page = request.GET.get("page")

    # Render the website
    return render(
        request,
        "network/index.html",
        {"newpost": False, "profile": False, "posts": p.page(page)},
    )


def edit_post(request):
    if request.method == "PUT":
        user = User.objects.get(id=request.user.id)
        data = json.loads(request.body)
        post = Post.objects.get(pk=data["postID"])

        if post.UserID == user:
            print("Match")
            post.message = data["message"]
            post.save(update_fields=["message"])
        return HttpResponse(status=204)


def like_post(request):
    if request.method == "PUT":
        user = User.objects.get(id=request.user.id)
        data = json.loads(request.body)
        post = Post.objects.get(pk=data["postID"])
        like = data["like"]

        if like:
            print("going to like")
            post.likedby.add(user)
        else:
            print("going to unlike")
            post.likedby.remove(user)
        return HttpResponse(status=204)


def profile(request, user_name):
    user_id = User.objects.filter(username=user_name).first().id
    # will resolve to 1 if current user follows the profile they are viewing
    follow_flag = Following.objects.filter(
        FollowerID=request.user.id, CreatorID=user_id
    ).count()

    if request.method == "PUT":
        data = json.loads(request.body)
        print("Pressed the following button")
        print(f"The data is: {data}")
        print(f"The user to follow is: {user_name}")
        print(f"The user following is: {request.user.id}")
        if data["follow"] and not follow_flag:
            print("going to follow")
            new_follower = Following()
            new_follower.CreatorID = User.objects.get(id=user_id)
            new_follower.FollowerID = User.objects.get(id=request.user.id)
            new_follower.save()
        elif not data["follow"] and follow_flag:
            print("going to unfollow")
            follower = Following.objects.filter(
                FollowerID=request.user.id, CreatorID=user_id
            )
            follower.delete()

        else:
            print("This should not be possible, need to debug")

        return HttpResponse(status=204)

    else:
        followers = Following.objects.filter(CreatorID=user_id).count()
        following = Following.objects.filter(FollowerID=user_id).count()
        users_posts = Post.objects.filter(UserID=user_id).order_by("-id")
        p = Paginator(users_posts, 10)
        page = 1
        if request.GET.get("page"):
            page = request.GET.get("page")

        button_text = "Follow"
        if request.user.id and follow_flag:
            button_text = "Unfollow"

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


def post(request):
    if request.method == "POST":
        new_post = Post()
        new_post.UserID = User.objects.get(id=request.user.id)
        new_post.message = request.POST.get("post-message")
        new_post.save()

    all_posts = Post.objects.all().order_by("-id")
    p = Paginator(all_posts, 10)
    page = 1
    if request.GET.get("page"):
        page = request.GET.get("page")

    return render(
        request,
        "network/index.html",
        {"newpost": True, "profile": False, "posts": p.page(page)},
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
