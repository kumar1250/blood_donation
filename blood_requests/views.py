import random
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import BloodRequest, Notification
from .forms import BloodRequestForm, OTPForm
from chat.models import ChatMessage

User = get_user_model()

# -------------------------------
# Utility: Generate 6-digit OTP
# -------------------------------
def _generate_otp():
    return f"{random.randint(100000, 999999):06d}"


# -------------------------------
# List all blood requests
# -------------------------------
@login_required
def request_list(request):
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
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = BloodRequestForm()
    return render(request, "blood_requests/request_form.html", {"form": form})


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

    # Generate OTP
    otp = _generate_otp()
    br.otp = otp
    br.otp_created_at = timezone.now()
    br.otp_verified = False
    br.save()

    donor_phone = getattr(request.user, "phone", "N/A")
    donor_address = getattr(request.user, "address", "N/A")

    # Email to requester
    subject = "Blood Request Donor Accepted - OTP"
    body = (
        f"Hello {br.name},\n\n"
        f"{request.user.username} has accepted your blood request.\n\n"
        f"🔑 OTP: {otp}\n"
        f"📞 Donor Phone: {donor_phone}\n"
        f"🏠 Donor Address: {donor_address}\n\n"
        "Regards,\nBlood Donation Team"
    )
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [br.email])
        messages.info(request, "📧 Donor details + OTP sent to requester by email.")
    except Exception as e:
        messages.error(request, f"Email failed: {e}")

    # Chat message
    try:
        ChatMessage.objects.create(
            sender=request.user,
            recipient=br.requester,
            content=f"🔑 OTP: {otp}\n📞 {donor_phone}\n🏠 {donor_address}"
        )
        messages.success(request, "✅ Donor details also sent via chat.")
    except Exception as e:
        messages.error(request, f"Chat message error: {e}")

    messages.success(request, "You accepted this request successfully.")
    return redirect("blood_requests:verify_otp", request_id=br.id)


# -------------------------------
# Verify OTP
# -------------------------------
@login_required
def verify_otp(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)

    if br.otp_created_at and timezone.now() - br.otp_created_at > timedelta(days=2):
        br.delete()
        messages.error(request, "❌ OTP expired. The request has been removed.")
        return redirect("blood_requests:request_list")

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            entered = form.cleaned_data["otp"].strip()
            if br.otp and br.otp == entered and br.otp_created_at and timezone.now() - br.otp_created_at <= timedelta(days=2):
                br.otp_verified = True
                br.save()

                # Notify requester
                subject = "Blood Request - Donor Confirmed"
                message = (
                    f"Hello {br.name},\n\n"
                    f"Your request has been confirmed by donors.\n"
                    f"Check your dashboard or chat for details.\n\n"
                    "Regards,\nBlood Donation Team"
                )
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [br.email])
                except Exception as e:
                    print("Email error:", e)

                # Optional: notify others with same blood group
                if br.blood_group:
                    same_users = User.objects.filter(blood_group=br.blood_group).exclude(id=br.requester_id)
                    notif_msg = (
                        f"Urgent: {br.blood_group} blood needed at {br.address} "
                        f"({br.reason or 'no reason'})"
                    )
                    for u in same_users:
                        Notification.objects.create(user=u, message=notif_msg)

                messages.success(request, "✅ OTP verified. Donor confirmed.")
                return redirect("blood_requests:request_list")
            else:
                messages.error(request, "❌ Invalid OTP or expired.")
    else:
        form = OTPForm()

    return render(request, "blood_requests/verify_otp.html", {"form": form, "br": br})


# -------------------------------
# Delete request
# -------------------------------
@login_required
def delete_request(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)

    if br.requester != request.user:
        messages.error(request, "❌ You cannot delete this request.")
        return redirect("blood_requests:request_list")

    br.delete()
    messages.success(request, "✅ Blood request deleted successfully.")
    return redirect("blood_requests:request_list")


# -------------------------------
# Placeholder for toggle location
# -------------------------------
@login_required
def toggle_location_share(request, request_id):
    messages.info(request, "⚠️ Live location feature is disabled.")
    return redirect("blood_requests:request_list")
