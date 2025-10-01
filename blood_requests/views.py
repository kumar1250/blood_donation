import random
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import BloodRequest, DonorLocation, Notification
from .forms import BloodRequestForm, OTPForm, ShareLocationForm
from chat.models import ChatMessage  # Your chat app

from django.http import JsonResponse



User = get_user_model()

# OTP generator
def _generate_otp():
    return f"{random.randint(100000, 999999):06d}"

# views.py (snippet)


@login_required
def request_list(request):
    # prefetch to reduce queries (accepted donors + donor locations + donor user)
    requests = BloodRequest.objects.all().order_by("-created_at").prefetch_related(
        "accepted_donors",
        "donor_locations__donor"
    )
    return render(request, "blood_requests/request_list.html", {"requests": requests})

# Create Request

@login_required
def request_form(request):
    if request.method == "POST":
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            br = form.save(commit=False)
            br.requester = request.user

            # --- Convert hidden lat/lng fields to float ---
            lat = request.POST.get("requester_lat")
            lng = request.POST.get("requester_lng")
            try:
                br.requester_lat = float(lat) if lat else None
                br.requester_lng = float(lng) if lng else None
            except ValueError:
                br.requester_lat = None
                br.requester_lng = None
            # ----------------------------------------------

            br.save()
            form.save_m2m()

            # --- Send notifications to users with same blood group ---
            if br.blood_group:
                same_users = User.objects.filter(blood_group=br.blood_group).exclude(id=request.user.id)
                notif_msg = f"Urgent: {br.blood_group} blood needed at {br.address} ({br.reason or 'N/A'})"

                for u in same_users:
                    # In-app notification
                    Notification.objects.create(user=u, message=notif_msg)

                    # Email
                    if u.email:
                        try:
                            send_mail(
                                subject=f"Blood Request - {br.blood_group} Needed",
                                message=notif_msg,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[u.email],
                                fail_silently=False
                            )
                        except Exception as e:
                            print(f"Email error for {u.email}: {e}")

                    # Chat app message
                    try:
                        ChatMessage.objects.create(
                            sender=request.user,
                            recipient=u,
                            content=notif_msg
                        )
                    except Exception as e:
                        print(f"Chat error for {u.username}: {e}")
            # ---------------------------------------------------------

            messages.success(request, "✅ Blood request created successfully! Notifications sent.")
            return redirect("blood_requests:request_list")
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = BloodRequestForm()

    return render(request, "blood_requests/request_form.html", {"form": form})

# Accept Request
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

    # Send Email + Chat
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

# Verify OTP
@login_required
def verify_otp(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)

    # Check if OTP expired (older than 2 days)
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

                # Send confirmation email
                try:
                    send_mail(
                        "Blood Request - Donor Confirmed",
                        f"Your request has been confirmed by donors.",
                        settings.DEFAULT_FROM_EMAIL,
                        [br.email]
                    )
                except Exception as e:
                    print("Email error:", e)

                # Notify other users with same blood group
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
# Delete Request
@login_required
def delete_request(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)
    if br.requester != request.user:
        messages.error(request, "❌ You cannot delete this request.")
        return redirect("blood_requests:request_list")
    br.delete()
    messages.success(request, "✅ Blood request deleted successfully.")
    return redirect("blood_requests:request_list")

# Donor Map
@login_required
def donor_map(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)
    donors_data = [
        {"lat": loc.lat, "lng": loc.lng, "username": loc.donor.username}
        for loc in br.donor_locations.all()
    ]
    return render(request, "blood_requests/donor_map.html", {"br": br, "donors_data": donors_data})

# Share Donor Location
@login_required
def share_location(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)
    donor = request.user
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
        form = ShareLocationForm(instance=loc_instance)

    return render(request, "blood_requests/share_location.html", {"form": form, "br": br})




@login_required
def update_location(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)
    donor = request.user

    if request.method == "POST":
        lat = request.POST.get("lat")
        lng = request.POST.get("lng")
        if lat and lng:
            loc, created = DonorLocation.objects.get_or_create(
                donor=donor,
                blood_request=br,
                defaults={"lat": lat, "lng": lng}
            )
            if not created:
                loc.lat = lat
                loc.lng = lng
                loc.save()
            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "error", "message": "No coordinates provided"})
    return JsonResponse({"status": "error", "message": "Invalid request"})




# View Requester's Location for donors
# Requester Map for Donors
@login_required
def requester_map(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)

    # Ensure requester location exists
    if br.requester_lat is None or br.requester_lng is None:
        messages.error(request, "Requester location is not available.")
        return redirect("blood_requests:request_list")

    return render(request, "blood_requests/requester_map.html", {"br": br})
