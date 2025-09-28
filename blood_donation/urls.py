from django.contrib import admin
from django.urls import path, include
from home import views as home_views  # For root URL

urlpatterns = [
    path('admin/', admin.site.urls),

    # Apps
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('requests/', include('blood_requests.urls', namespace='blood_requests')),
    path('camps/', include('blood_camp.urls', namespace='blood_camp')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('live/', include('live_tracking.urls', namespace='live_tracking')),

    # Home page
    path('', home_views.home, name='home'),
]
