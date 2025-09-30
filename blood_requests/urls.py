from django.urls import path
from . import views

app_name = "blood_requests"

urlpatterns = [
    path("", views.request_list, name="request_list"),
    path("new/", views.request_form, name="request_form"),
    path("<int:request_id>/delete/", views.delete_request, name="delete_request"),
    path("<int:request_id>/accept/", views.accept_request, name="accept_request"),
    path("<int:request_id>/verify_otp/", views.verify_otp, name="verify_otp"),
    path("donor-map/<int:request_id>/", views.donor_map, name="donor_map"),
    path("share-location/<int:request_id>/", views.share_location, name="share_location"),

    # Live location updates
    path("update-location/", views.update_location, name="update_location"),
]
