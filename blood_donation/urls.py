# blood_donation/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # accounts app handles login/signup/profile
    path("accounts/", include("accounts.urls")),

    # chat app
    path("chat/", include("chat.urls")),

    # blood requests
    path("requests/", include("blood_requests.urls")),

    # home page (root)
    path("", include("home.urls")),  # keep this last as the default root
]

