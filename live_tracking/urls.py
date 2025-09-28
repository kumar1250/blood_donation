from django.urls import path
from . import views

app_name = "live_tracking"

urlpatterns = [
    path("map/<int:request_id>/", views.map_view, name="map_view"),
    path("donor/<int:donor_id>/", views.donor_location_view, name="donor_location_view"),
    path("donors/<int:request_id>/", views.donors_for_request, name="donors_for_request"),
    path("update_location/", views.update_location, name="update_location"),

    # ✅ New path for live map showing all donors
    path("donor_map/", views.donor_map, name="donor_map"),
    path("donor_data_json/", views.donor_data_json, name="donor_data_json"),

]
