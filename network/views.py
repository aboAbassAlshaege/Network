from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import *


def index(request):
    return render(request, "network/index.html", {
        "posts": Post.objects.all()
    })

@login_required
def create_post(request):
    if request.method == 'POST':
      content = request.POST.get('content', '').strip()
      if not content:
          return JsonResponse({"error": "content can not be empty"}, status=400)
      post = Post.objects.create(author=request.user, content=content)
      return JsonResponse({"message": "Post created successfully", "post": {
        "author": post.author.username,
        "content": post.content,
        "date_stamp": post.date_stamp.strftime("%Y-%m-%D %H:%M:%S"),
        "total_likes": post.total_likes()
      }}, status=200)
    return JsonResponse({"error": "Invalid request"}, status=400)
  
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
