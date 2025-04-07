
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("page/<int:page_num>", views.index, name="page"),
    path("create_post", views.create_post, name="create_post"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("update_post", views.update_post, name="update_post"),
    path("profiles/<str:specific_author>", views.profile, name="profile"),
    path("profiles/<str:specific_author>/follow", views.follow, name="follow")
]
