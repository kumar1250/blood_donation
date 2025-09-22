from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.chat_home, name="chat_home"),
    path("<str:username>/", views.chat_view, name="chat_view"),
    path("follow/<str:username>/", views.follow_toggle, name="follow_toggle"),
]
