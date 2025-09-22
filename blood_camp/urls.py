from django.urls import path
from . import views

app_name = "blood_camp"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("camps/", views.camp_list, name="camp_list"),
    path("new/", views.create_camp, name="create_camp"),
    path("<int:camp_id>/", views.camp_detail, name="camp_detail"),
]
