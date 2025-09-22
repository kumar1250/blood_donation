from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Apps with namespaces
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('chat/', include(('chat.urls', 'chat'), namespace='chat')),
    path('requests/', include(('blood_requests.urls', 'blood_requests'), namespace='blood_requests')),
    path('camps/', include(('blood_camp.urls', 'blood_camp'), namespace='blood_camp')),
    path('', include(('home.urls', 'home'), namespace='home')),  # Home page
]
