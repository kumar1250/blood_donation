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
from chat.models import ChatMessage   # ✅ Import your chat model

User = get_user_model()


# ✅ Generate a 6-digit OTP
def _generate_otp():
    return f"{random.randint(100000, 999999):06d}"


# ✅ List all requests
@login_required
def request_list(request):
    requests = BloodRequest.objects.all().order_by("-created_at")
    return render(request, "blood_requests/request_list.html", {"requests": requests})


@login_required
def create_request(request):
    form = BloodRequestForm()
    if request.method == "POST":
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            br = form.save(commit=False)
            br.requester = request.user
            br.save()
            messages.success(request, "✅ Blood request created successfully!")
            return redirect("request_list")
    return render(request, "blood_requests/request_form.html", {"form": form})


# ✅ Accept a request (send OTP + phone + address + share to chat)
@login_required
def accept_request(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)

    # Generate and store OTP
    otp = _generate_otp()
    br.otp = otp
    br.otp_created_at = timezone.now()
    br.accepted_by = request.user
    br.otp_verified = False
    br.save()

    # Build message
    subject = "Your Blood Request OTP (verify to confirm donor)"
    message = (
        f"Hello {br.name},\n\n"
        f"{request.user.username} has accepted to be a donor for your request.\n\n"
        f"📌 OTP: {otp}\n"
        f"📞 Donor Phone: {getattr(request.user, 'phone', 'N/A')}\n"
        f"🏠 Donor Address: {getattr(request.user, 'address', 'N/A')}\n\n"
        f"Regards,\nBlood Donation Team"
    )

    # Send OTP email
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [br.email])
        messages.info(request, "📧 OTP + donor details have been sent to the requester email.")
    except Exception as e:
        messages.error(request, f"Email sending failed: {e}")

    # ✅ Also send same message into chat
    try:
        ChatMessage.objects.create(
            sender=request.user,
            receiver=br.requester,
            message=f"🔑 OTP: {otp}\n📞 Phone: {getattr(request.user, 'phone', 'N/A')}\n🏠 Address: {getattr(request.user, 'address', 'N/A')}"
        )
    except Exception as e:
        print("Chat save error:", e)

    return redirect("verify_otp", request_id=br.id)


# ✅ Verify OTP
# ✅ Verify OTP
@login_required
def verify_otp(request, request_id):
    br = get_object_or_404(BloodRequest, id=request_id)

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            entered = form.cleaned_data["otp"].strip()

            # Check OTP validity (15 minutes expiry)
            if (
                br.otp
                and br.otp == entered
                and br.otp_created_at
                and timezone.now() - br.otp_created_at <= timedelta(minutes=15)
            ):
                # ✅ OTP is correct → delete request after confirming
                br.otp_verified = True
                br.save()

                # Notify requester (email)
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

                # Optional: notify all same blood group users
                if br.blood_group:
                    same_users = User.objects.filter(
                        blood_group=br.blood_group
                    ).exclude(id=br.requester_id)
                    notif_msg = (
                        f"Urgent: {br.blood_group} blood needed at {br.address} "
                        f"({br.reason or 'no reason'})"
                    )
                    for u in same_users:
                        Notification.objects.create(user=u, message=notif_msg)

                # ✅ Delete the request after success
                br.delete()

                messages.success(request, "✅ OTP verified, donor confirmed & request closed.")
                return redirect("request_list")
            else:
                messages.error(request, "❌ Invalid or expired OTP.")
    else:
        form = OTPForm()

    return render(request, "blood_requests/verify_otp.html", {"form": form, "br": br})
