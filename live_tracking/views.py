from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from .models import LiveLocation
from blood_requests.models import BloodRequest
from django.contrib.auth import get_user_model
import json

User = get_user_model()

# Update donor's live location (AJAX)
@login_required
def update_location(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        data = json.loads(request.body)
        lat = float(data.get("latitude"))
        lng = float(data.get("longitude"))
        is_sharing = bool(data.get("is_sharing", True))
    except:
        return JsonResponse({"error": "Invalid data"}, status=400)

    loc, _ = LiveLocation.objects.get_or_create(user=request.user)
    loc.latitude = lat
    loc.longitude = lng
    loc.is_sharing = is_sharing
    loc.save()
    return JsonResponse({"status": "ok"})


# Donors and requester locations for a blood request
@login_required
def donors_for_request(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)

    if request.user != br.requester and request.user not in br.accepted_donors.all():
        return HttpResponseForbidden("Not allowed")

    donors_data = []
    for donor in br.accepted_donors.all():
        try:
            loc = donor.live_location
            if loc.is_sharing and loc.latitude and loc.longitude:
                donors_data.append({
                    "id": donor.id,
                    "username": donor.username,
                    "lat": loc.latitude,
                    "lng": loc.longitude
                })
        except LiveLocation.DoesNotExist:
            continue

    requester_loc = None
    if br.requester_lat and br.requester_lng:
        requester_loc = {
            "lat": br.requester_lat,
            "lng": br.requester_lng
        }

    return JsonResponse({"donors": donors_data, "requester": requester_loc})


# View map for a blood request
@login_required
def map_view(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)
    return render(request, "live_tracking/map_view.html", {"br": br})


# Optional: individual donor location
@login_required
def donor_location_view(request, donor_id):
    donor = get_object_or_404(User, id=donor_id)
    try:
        loc = donor.live_location
        if loc.is_sharing and loc.latitude and loc.longitude:
            return JsonResponse({
                "id": donor.id,
                "username": donor.username,
                "lat": loc.latitude,
                "lng": loc.longitude
            })
    except LiveLocation.DoesNotExist:
        pass
    return JsonResponse({"error": "No location"}, status=404)



@login_required
def donor_map(request):
    """
    Show a map with all donors who are sharing their live location.
    """
    donors_data = []
    users = User.objects.all()
    for user in users:
        try:
            loc = user.live_location
            if loc.is_sharing and loc.latitude and loc.longitude:
                donors_data.append({
                    "id": user.id,
                    "username": user.username,
                    "lat": loc.latitude,
                    "lng": loc.longitude
                })
        except LiveLocation.DoesNotExist:
            continue

    return render(request, "live_tracking/donor_map.html", {"donors": donors_data})



@login_required
def donor_data_json(request):
    donors_data = []
    users = User.objects.all()
    for user in users:
        try:
            loc = user.live_location
            if loc.is_sharing and loc.latitude and loc.longitude:
                donors_data.append({
                    "user": {"id": user.id, "username": user.username},
                    "latitude": loc.latitude,
                    "longitude": loc.longitude
                })
        except LiveLocation.DoesNotExist:
            continue

    return JsonResponse({"donors": donors_data})
