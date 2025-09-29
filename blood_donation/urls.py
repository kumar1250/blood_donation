from django.contrib import admin
from django.urls import path, include
from home import views as home_views  # For root URL

urlpatterns = [
    path("admin/", admin.site.urls),

    # Apps
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("blood_requests/", include("blood_requests.urls", namespace="blood_requests")),
    path("blood_camp/", include("blood_camp.urls", namespace="blood_camp")),
    path("chat/", include("chat.urls", namespace="chat")),


    # Home page
    path("", home_views.home, name="home"),
]
