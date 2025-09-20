from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='chat_home'),  # Home page
    path('<str:username>/', views.chat_view, name='chat'),  # Chat with user
]
