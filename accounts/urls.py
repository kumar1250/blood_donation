from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("forgot/", views.forgot_password, name="forgot_password"),
    path("verify_otp/", views.verify_otp, name="verify_otp"),
    path("reset_password/", views.reset_password, name="reset_password"),

    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.home, name="home"),

    path('accounts/login/', views.login_view, name='login_alt'),
    path('login/', views.login_view, name='login'),
    # ... other urls
    # Follow system
    path("follow/<str:username>/", views.follow_user, name="follow_user"),
    path("unfollow/<str:username>/", views.unfollow_user, name="unfollow_user"),
    path("followers/", views.followers_list, name="followers_list"),
]
