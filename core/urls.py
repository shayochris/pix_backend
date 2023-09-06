from django.urls import path
from . import views
urlpatterns=[
    path("tests/",views.tests),
    path("tests/<int:id>",views.test),
    path("signup/",views.signup),
    path("login/",views.login),
    path("user/<str:id>",views.user),
    path("home/",views.home),
    path("settings/",views.settings),
    path("password/",views.password),
    path("posts/",views.posts),
    path("likepost/",views.likepost),
    path("likes/<str:id>",views.likes),
    path("comments/<str:id>",views.comments),
    path("follow/<str:id>",views.follow),
    path("followers/<str:id>",views.followers),
    path("following/<str:id>",views.following),
]