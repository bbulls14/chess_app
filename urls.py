from django.urls import path
from chess_app import views

urlpatterns = [
    path("", views.home, name="home"),
]