from django.urls import path
from . import views

app_name = "blood_requests"

urlpatterns = [
    path("", views.request_list, name="request_list"),  # list all requests
    path("new/", views.request_form, name="request_form"),  # create request
    path("accept/<int:request_id>/", views.accept_request, name="accept_request"),
    path("verify_otp/<int:request_id>/", views.verify_otp, name="verify_otp"),
]
