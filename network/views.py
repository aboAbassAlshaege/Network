from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.generic import ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import *

class BasePostList (ListView):
    model = Post
    template_name = "network/index.html"
    context_object_name = "posts"
    paginate_by = 10
    ordering = ["-date_stamp"]
    def get_context_data(self, **kwargs):
        content = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # make a dictionary, keys represent posts and values are either true or false
            # to indicate if the post is liked by the user who made the like request
            is_liked_by_user = {}
            for post in content["posts"]:
                is_liked_by_user[post.id] = post.is_liked_by(self.request.user)
            content["is_liked_by_user"] = is_liked_by_user
        return content
    
# def index(request, page_num=1):
#     paginator = Paginator(Post.objects.all().order_by("-date_stamp"), 10)
#     return render(request, "network/index.html", {
#         "page_obj": paginator.get_page(page_num),
#         "show_pagination": True,
#         "show_post_author": True
#     })
def toggle_like (request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"redirect": "/login"}, status=401)
        else:
            # get the post id
            post_id = request.POST.get("target_post_id")
            if not post_id:
                return JsonResponse({"error": "Missing post ID"}, status=400)
            # get the target post from database
            target_post = get_object_or_404(Post, pk=post_id)

            like, created = Like.objects.get_or_create(user=request.user, post=target_post)
            if created:
                return JsonResponse({"message": "You liked this post", "liked": True, "total_likes":target_post.total_likes()}, status=200)
            else:
                like.delete()
                return JsonResponse({"message": "You unliked this post", "liked": False, "total_likes":target_post.total_likes()}, status=200)
    else:
        return JsonResponse({"error": "Invalid Request"}, status=400)

class FollowingView(BasePostList):
    template_name = 'network/following.html'
    def get_queryset(self):
        following_users = self.request.user.profile.following.values_list("user", flat=True)
        return Post.objects.filter(author__in=following_users).order_by("-date_stamp")

def follow (request, profile_owner):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"redirect": "/login"}, status=401)
        target_name = request.POST.get("profile_page_owner_username")
        try:
            target_profile = get_object_or_404(User, username=target_name)
            is_following = request.user.profile.following.filter(id=target_profile.profile.id).exists()
            if request.user != target_profile:
                if not is_following:
                    request.user.profile.following.add(target_profile.profile)
                    followers_count = target_profile.profile.followers.count()
                    is_following = True
                    return JsonResponse({"message": "Followed Successfuly", "follow_status": is_following, "followers_count": followers_count})
                else:
                    request.user.profile.following.remove(target_profile.profile)
                    followers_count = target_profile.profile.followers.count()
                    is_following = False
                    return JsonResponse({"message": "Unfollowed Successfully", "follow_status": is_following, "followers_count": followers_count})
        except User.DoesNotExist:
            return JsonResponse({"error": "The profile owner doesn't exsit"}, status=400)
    else:
        return JsonResponse({"error": "Invalid Request"})

class ProfileView(BasePostList):
    template_name = "network/profile.html"
    def get_queryset(self):
        self.profile_owner = get_object_or_404(User, username=self.kwargs["profile_owner"])
        return Post.objects.filter(author=self.profile_owner).order_by("-date_stamp")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            follow_status = user.profile.following.filter(id=self.profile_owner.profile.id).exists()
        else:
            follow_status = False
        context["profile_owner"] = self.profile_owner
        context["follow_status"] = follow_status
        return context
    
# def profile(request, specific_author):
#     try:
#         specific_author = User.objects.get(username=specific_author)
#         posts = Post.objects.filter(author=specific_author).order_by("-date_stamp")
#         if request.user.is_authenticated:
#             follow_status = request.user.profile.following.filter(id=specific_author.profile.id).exists()
#         else:
#             follow_status = False

#         return render(request, "network/profile.html", {
#             "specific_author": specific_author,
#             "posts": posts,
#             "follow_status": follow_status
#         })
#     except User.DoesNotExist:
#         return HttpResponseRedirect(reverse(index))

@login_required
def create_post(request):
    if request.method == 'POST':
      content = request.POST.get('content', '').strip()
      if not content:
          return JsonResponse({"error": "content can not be empty"}, status=400)
      post = Post.objects.create(author=request.user, content=content)
      return JsonResponse({"message": "Post created successfully", "post": {
        "id": post.id,
        "author": post.author.username,
        "content": post.content,
        "date_stamp": post.date_stamp.strftime("%Y-%m-%D %H:%M:%S"),
        "total_likes": post.total_likes()
      }}, status=200)
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def update_post(request):
    if request.method == 'POST':
      updated_content = request.POST.get('updated_content', '').strip()
      if not updated_content:
          return JsonResponse({"error": "content can not be empty"}, status=400)
      post_id = request.POST.get("post_id")
      try:
          post = Post.objects.get(pk=post_id)
          if request.user != post.author:
              return JsonResponse({"error": "Permission Denied"})
          post.content = updated_content
          post.save()
          return JsonResponse({"message": "Post updated successfully", "post": {
            "updated_content": post.content,
            "date_stamp": post.updated_at.strftime("%Y-%m-%D %H:%M:%S"),
          }}, status=200)
      except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found or unauthorized"}, status=400)
    else:
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
