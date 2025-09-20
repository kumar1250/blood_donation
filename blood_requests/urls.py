from django.urls import path
from . import views

urlpatterns = [
    path("new/", views.create_request, name="create_request"),   # Create a new request
    path("", views.request_list, name="request_list"),           # List all requests
    path("list/", views.request_list, name="request_list_alt"),  # Alternate list
    path("<int:request_id>/accept/", views.accept_request, name="accept_request"),
    path("<int:request_id>/verify/", views.verify_otp, name="verify_otp"),
]

