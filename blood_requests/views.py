import random, json
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

from .models import BloodRequest
from .forms import BloodRequestForm, OTPForm
from chat.models import ChatMessage
from live_tracking.models import LiveLocation

User = get_user_model()


# -------------------------------
# Generate 6-digit OTP
# -------------------------------
def _generate_otp():
    return f"{random.randint(100000, 999999):06d}"


# -------------------------------
# List all blood requests
# -------------------------------
@login_required
def request_list(request):
    BloodRequest.objects.filter(
        otp_created_at__isnull=False,
        otp_verified=False,
        otp_created_at__lt=timezone.now() - timedelta(days=2)
    ).delete()
    requests = BloodRequest.objects.all().order_by("-created_at")
    return render(request, "blood_requests/request_list.html", {"requests": requests})


# -------------------------------
# Create a new blood request
# -------------------------------
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
            messages.error(request, "❌ Please correct the errors.")
    else:
        form = BloodRequestForm()
    return render(request, "blood_requests/request_form.html", {"form": form})


# -------------------------------
# Delete a blood request
# -------------------------------
@login_required
def delete_request(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)
    if request.user != br.requester:
        return HttpResponseForbidden("❌ Not allowed")
    br.delete()
    messages.success(request, "✅ Blood request deleted.")
    return redirect("blood_requests:request_list")


# -------------------------------
# Accept a request
# -------------------------------
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

    # Ensure donor has a LiveLocation object
    LiveLocation.objects.get_or_create(user=request.user, defaults={"is_sharing": False})

    donor_phone = getattr(request.user, "phone", "N/A")
    donor_address = getattr(request.user, "address", "N/A")

    try:
        subject = "Blood Request - Donor Accepted"
        body = f"{request.user.username} accepted your request.\nOTP: {otp}\nPhone: {donor_phone}\nAddress: {donor_address}"
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [br.email])
    except:
        pass

    try:
        ChatMessage.objects.create(
            sender=request.user,
            recipient=br.requester,
            content=f"🔑 OTP: {otp}\n📞 Phone: {donor_phone}\n🏠 Address: {donor_address}"
        )
    except:
        pass

    messages.success(request, "✅ You accepted this request. Click 'Share Live Location' to start.")
    return redirect("blood_requests:request_list")


# -------------------------------
# Toggle Live Location Sharing
# -------------------------------
@login_required
def toggle_location_share(request, request_id):
    loc, _ = LiveLocation.objects.get_or_create(user=request.user)
    loc.is_sharing = not loc.is_sharing
    loc.save()
    status = "started" if loc.is_sharing else "stopped"
    messages.success(request, f"✅ Live location sharing {status}.")
    return redirect("blood_requests:request_list")


# -------------------------------
# Verify OTP
# -------------------------------
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
                messages.success(request, "✅ OTP verified. Donor confirmed.")
                return redirect("blood_requests:request_list")
            else:
                messages.error(request, "❌ Invalid OTP.")
    else:
        form = OTPForm()

    return render(request, "blood_requests/verify_otp.html", {"form": form, "br": br})


# -------------------------------
# Update Requester Location (AJAX)
# -------------------------------
@csrf_exempt
@login_required
def update_requester_location(request, request_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    br = get_object_or_404(BloodRequest, id=request_id)
    if br.requester != request.user:
        return HttpResponseForbidden("❌ Only requester can update their location")

    try:
        data = json.loads(request.body)
        lat = float(data.get("latitude"))
        lng = float(data.get("longitude"))
    except:
        return JsonResponse({"error": "Invalid data"}, status=400)

    br.requester_lat = lat
    br.requester_lng = lng
    br.save(update_fields=["requester_lat", "requester_lng"])

    return JsonResponse({"status": "ok"})


@login_required
def home(request):
    # Redirect to request list (or render a homepage template)
    return redirect("blood_requests:request_list")