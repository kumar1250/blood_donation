# blood_requests/views.py

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
from chat.models import ChatMessage  # Chat model





from django.utils import timezone

User = get_user_model()


# -------------------------------
# Utility: Generate 6-digit OTP
# -------------------------------
def _generate_otp():
    return f"{random.randint(100000, 999999):06d}"


# -------------------------------
# List all blood requests
# -------------------------------

def request_list(request):
    # Delete all requests that already have a verified OTP
    BloodRequest.objects.filter(otp_verified=True).delete()

    # Delete requests where OTP expired (more than 2 days old)
    BloodRequest.objects.filter(
        otp_created_at__isnull=False,
        otp_verified=False,
        otp_created_at__lt=timezone.now() - timedelta(days=2)
    ).delete()

    # Show only active requests
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
            br.requester = request.user  # the logged-in user
            br.save()
            messages.success(request, "✅ Blood request created successfully!")
            return redirect("blood_requests:request_list")  # redirect to list
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = BloodRequestForm()

    return render(request, "blood_requests/request_form.html", {"form": form})
# -------------------------------
# Accept a request (send OTP + donor info + chat)
# -------------------------------
# blood_requests/views.py

# blood_requests/views.py  (replace only the accept_request function)


# other imports in your file remain...
# from .models import BloodRequest, Notification
# from .forms import BloodRequestForm, OTPForm
# etc.

@login_required
def accept_request(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)

    # Generate OTP and update the BloodRequest
    otp = _generate_otp()
    br.otp = otp
    br.otp_created_at = timezone.now()
    br.accepted_by = request.user
    br.otp_verified = False
    br.save()

    # Build plain-text message for email & chat
    donor_phone = getattr(request.user, "phone", "N/A")
    donor_address = getattr(request.user, "address", "N/A")

    subject = "Your Blood Request OTP (verify to confirm donor)"
    body = (
        f"Hello {br.name},\n\n"
        f"{request.user.username} has accepted to be a donor for your request.\n\n"
        f"🔑 OTP: {otp}\n"
        f"📞 Donor Phone: {donor_phone}\n"
        f"🏠 Donor Address: {donor_address}\n\n"
        "Regards,\nBlood Donation Team"
    )

    # 1) Send email (keep this, handle error)
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [br.email])
        messages.info(request, "📧 OTP + donor details have been sent to the requester email.")
    except Exception as e:
        # show a message and continue — we still want to attempt saving to chat
        messages.error(request, f"Email sending failed: {e}")

    # 2) Save message into ChatMessage (chat app)
    try:
        # import here to avoid circular import issues at module load
        from chat.models import ChatMessage

        ChatMessage.objects.create(
            sender=request.user,
            recipient=br.requester,   # NOTE: 'recipient' (not 'receiver')
            content=(
                f"🔑 OTP: {otp}\n"
                f"📞 Donor Phone: {donor_phone}\n"
                f"🏠 Donor Address: {donor_address}"
            )
        )
        messages.success(request, "✅ Donor details also sent via chat.")
    except Exception as e:
        # don't crash — but show error so you know what went wrong
        messages.error(request, f"Could not save chat message: {e}")
        # for debugging you can also print(e) or log it

    # After sending, go to OTP verification page (same as before)
    return redirect("blood_requests:verify_otp", request_id=br.id)

# -------------------------------
# Verify OTP
# -------------------------------

User = get_user_model()

@login_required
def verify_otp(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)

    # Check if OTP expired (more than 2 days old)
    if br.otp_created_at and timezone.now() - br.otp_created_at > timedelta(days=2):
        br.delete()  # Delete request if expired
        messages.error(request, "❌ OTP expired. The request has been deleted.")
        return redirect("blood_requests:request_list")

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            entered = form.cleaned_data["otp"].strip()
            # Check OTP + 2 days expiry
            if (
                br.otp
                and br.otp == entered
                and br.otp_created_at
                and timezone.now() - br.otp_created_at <= timedelta(days=2)
            ):
                # OTP correct → confirm donor
                br.otp_verified = True
                br.save()

                # Notify requester via email
                subject = "Your Blood Request - Donor Confirmed"
                message = (
                    f"Hello {br.name},\n\n"
                    f"Your request has been confirmed by {br.accepted_by.username}.\n"
                    f"Contact details:\n"
                    f"Email: {br.accepted_by.email}\n"
                    f"Phone: {getattr(br.accepted_by, 'phone', 'N/A')}\n\n"
                    "Please contact the donor.\n\nRegards,\nBlood Donation Team"
                )
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [br.email])
                except Exception as e:
                    print("Email error:", e)

                # Optional: notify all users with same blood group
                if br.blood_group:
                    same_users = User.objects.filter(
                        blood_group=br.blood_group
                    ).exclude(id=br.requester_id)
                    notif_msg = (
                        f"Urgent: {br.blood_group} blood needed at {br.address} "
                        f"({br.reason or 'no reason'})"
                    )
                    for u in same_users:
                        # Assuming you have a Notification model
                        Notification.objects.create(user=u, message=notif_msg)

                # Delete request after success
                br.delete()

                messages.success(request, "✅ OTP verified, donor confirmed & request closed.")
                return redirect("blood_requests:request_list")
            else:
                messages.error(request, "❌ Invalid OTP or expired (older than 2 days).")
    else:
        form = OTPForm()

    return render(request, "blood_requests/verify_otp.html", {"form": form, "br": br})
