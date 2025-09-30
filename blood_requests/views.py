import random
import json
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse

from .models import BloodRequest, Notification, DonorLocation, LiveLocation
from .forms import BloodRequestForm, OTPForm, ShareLocationForm
from chat.models import ChatMessage

User = get_user_model()

# -------------------
# OTP generator
# -------------------
def _generate_otp():
    return f"{random.randint(100000, 999999):06d}"

# -------------------
# Blood Request List
# -------------------
@login_required
def request_list(request):
    requests = BloodRequest.objects.all().order_by("-created_at")
    return render(request, "blood_requests/request_list.html", {"requests": requests})

# -------------------
# Create Blood Request
# -------------------
@login_required
def request_form(request):
    if request.method == "POST":
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            br = form.save(commit=False)
            br.requester = request.user
            br.save()
            messages.success(request, "✅ Blood request created successfully!")
            return redirect("blood_requests:request_list")
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = BloodRequestForm()
    return render(request, "blood_requests/request_form.html", {"form": form})

# -------------------
# Accept Request
# -------------------
@login_required
def accept_request(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)
    if br.accepted_donors.filter(id=request.user.id).exists():
        messages.warning(request, "⚠️ You already accepted this request.")
        return redirect("blood_requests:request_list")

    br.accepted_donors.add(request.user)
    otp = _generate_otp()
    br.otp = otp
    br.otp_created_at = timezone.now()
    br.otp_verified = False
    br.save()

    donor_phone = getattr(request.user, "phone", "N/A")
    donor_address = getattr(request.user, "address", "N/A")

    try:
        send_mail(
            f"Blood Request Donor Accepted - OTP",
            f"{request.user.username} accepted your request.\nOTP: {otp}\nPhone: {donor_phone}\nAddress: {donor_address}",
            settings.DEFAULT_FROM_EMAIL,
            [br.email]
        )
        messages.info(request, "📧 Donor details + OTP sent via email.")
    except Exception as e:
        messages.error(request, f"Email failed: {e}")

    try:
        ChatMessage.objects.create(
            sender=request.user,
            recipient=br.requester,
            content=f"OTP: {otp}\nPhone: {donor_phone}\nAddress: {donor_address}"
        )
        messages.success(request, "✅ Donor details sent via chat.")
    except Exception as e:
        messages.error(request, f"Chat message error: {e}")

    messages.success(request, "You accepted this request successfully.")
    return redirect("blood_requests:verify_otp", request_id=br.id)

# -------------------
# Verify OTP
# -------------------
@login_required
def verify_otp(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)
    if br.otp_created_at and timezone.now() - br.otp_created_at > timedelta(days=2):
        br.delete()
        messages.error(request, "❌ OTP expired. Request removed.")
        return redirect("blood_requests:request_list")

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            entered = form.cleaned_data["otp"].strip()
            if br.otp == entered:
                br.otp_verified = True
                br.save()

                try:
                    send_mail(
                        "Blood Request - Donor Confirmed",
                        f"Your request has been confirmed by donors.",
                        settings.DEFAULT_FROM_EMAIL,
                        [br.email]
                    )
                except Exception as e:
                    print("Email error:", e)

                # Notify same blood group users
                if br.blood_group:
                    same_users = User.objects.filter(blood_group=br.blood_group).exclude(id=br.requester_id)
                    notif_msg = f"Urgent: {br.blood_group} blood needed at {br.address} ({br.reason or 'N/A'})"
                    for u in same_users:
                        Notification.objects.create(user=u, message=notif_msg)

                messages.success(request, "✅ OTP verified. Donor confirmed.")
                return redirect("blood_requests:request_list")
            else:
                messages.error(request, "❌ Invalid OTP or expired.")
    else:
        form = OTPForm()

    return render(request, "blood_requests/verify_otp.html", {"form": form, "br": br})

# -------------------
# Delete Request
# -------------------
@login_required
def delete_request(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)
    if br.requester != request.user:
        messages.error(request, "❌ You cannot delete this request.")
        return redirect("blood_requests:request_list")
    br.delete()
    messages.success(request, "✅ Blood request deleted successfully.")
    return redirect("blood_requests:request_list")

# -------------------
# Donor Map
# -------------------
@login_required
def donor_map(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)
    if request.GET.get("json") == "1":
        requester_data = None
        if br.requester_lat and br.requester_lng:
            requester_data = {
                "lat": br.requester_lat,
                "lng": br.requester_lng,
                "username": br.requester.username,
                "color": "red" if br.emergency else "blue"
            }

        donors_data = [
            {
                "id": loc.donor.id,
                "lat": loc.lat,
                "lng": loc.lng,
                "username": loc.donor.username,
                "color": "green"
            } for loc in br.donor_locations.all()
        ]
        return JsonResponse({"requester": requester_data, "donors": donors_data})

    return render(request, "blood_requests/donor_map.html", {"br": br})

# -------------------
# Share Donor Location per Request
# -------------------
@login_required
def share_location(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)
    donor = request.user

    # Try to get existing location
    try:
        loc_instance = DonorLocation.objects.get(donor=donor, blood_request=br)
    except DonorLocation.DoesNotExist:
        loc_instance = None

    if request.method == "POST":
        form = ShareLocationForm(request.POST, instance=loc_instance)
        if form.is_valid():
            share = form.save(commit=False)
            share.donor = donor
            share.blood_request = br
            share.save()
            messages.success(request, "✅ Location shared successfully!")
            return redirect("blood_requests:request_list")
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        # Only create form, don't save yet
        initial_data = {}
        # Pre-fill with donor's live location if available
        if hasattr(donor, "livelocation"):
            initial_data["lat"] = donor.livelocation.lat
            initial_data["lng"] = donor.livelocation.lng
        form = ShareLocationForm(instance=loc_instance, initial=initial_data)

    return render(request, "blood_requests/share_location.html", {"form": form, "br": br})

# -------------------
# Update donor global live location
# -------------------
@login_required
def update_location(request):
    if request.method == "POST":
        data = json.loads(request.body)
        lat = data.get("lat")
        lng = data.get("lng")
        if lat is not None and lng is not None:
            loc, _ = LiveLocation.objects.get_or_create(user=request.user)
            loc.lat = lat
            loc.lng = lng
            loc.save()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "failed", "message": "POST required"})
