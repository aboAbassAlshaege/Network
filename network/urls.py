
from django.urls import path

from . import views

urlpatterns = [
    path("", views.BasePostList.as_view(), name="index"),
    path("create_post", views.create_post, name="create_post"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("update_post", views.update_post, name="update_post"),
    path("profiles/<str:profile_owner>", views.ProfileView.as_view(), name="profile"),
    path("profiles/<str:profile_owner>/follow", views.follow, name="follow"),
    path("following", views.FollowingView.as_view(), name="following"),
    path("toggle_like", views.toggle_like, name="toggle_like"),
]
