from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
import random
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from .models import Follow
from .forms import RegisterForm

User = get_user_model()

def signup(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "✅ Registration successful! Please login.")
            return redirect('accounts:login')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'accounts/signup.html', {'form': form})

def send_otp(email):
    otp = str(random.randint(1000, 9999))
    cache.set(email, otp, timeout=300)  # 5 minutes
    subject = "Your OTP Code"
    message = f"Your OTP is {otp}. It will expire in 5 minutes."
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER)
    recipient_list = [email]
    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        # log error in real app; propagate a message to the user is done in caller
        print("send_otp email error:", e)

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            send_otp(email)
            request.session["email"] = email
            messages.info(request, "✅ OTP sent to your email.")
            return redirect("accounts:verify_otp")
        else:
            messages.error(request, "❌ Email not registered")
    return render(request, "accounts/forgot_password.html")

def verify_otp(request):
    email = request.session.get("email")
    if not email:
        messages.error(request, "❌ Session expired. Try again.")
        return redirect("accounts:forgot_password")

    if request.method == "POST":
        otp = request.POST.get("otp")
        cached_otp = cache.get(email)
        if cached_otp == otp:
            messages.success(request, "✅ OTP verified. Set your new password.")
            return redirect("accounts:reset_password")
        else:
            messages.error(request, "❌ Invalid OTP")
    return render(request, "accounts/verify_otp.html")

def reset_password(request):
    email = request.session.get("email")
    if not email:
        messages.error(request, "❌ Session expired. Try again.")
        return redirect("accounts:forgot_password")

    if request.method == "POST":
        new_password = request.POST.get("password")
        user = User.objects.filter(email=email).first()
        if user:
            user.password = make_password(new_password)
            user.save()
            messages.success(request, "✅ Password updated successfully. Login again.")
            request.session.pop("email", None)
            return redirect("accounts:login")
        else:
            messages.error(request, "❌ Something went wrong. Try again.")
            return redirect("accounts:forgot_password")
    return render(request, "accounts/reset_password.html")

@login_required
def home(request):
    return render(request, "home/home.html")

@login_required
def follow_user(request, username):
    other_user = User.objects.filter(username=username).first()
    if other_user and other_user != request.user:
        Follow.objects.get_or_create(follower=request.user, following=other_user)
    # go back to previous page to keep UX smooth
    return redirect(request.META.get('HTTP_REFERER', 'home:home'))

@login_required
def unfollow_user(request, username):
    other_user = User.objects.filter(username=username).first()
    if other_user:
        Follow.objects.filter(follower=request.user, following=other_user).delete()
    return redirect(request.META.get('HTTP_REFERER', 'home:home'))

@login_required
def followers_list(request):
    followers_qs = Follow.objects.filter(following=request.user).select_related('follower')
    following_qs = Follow.objects.filter(follower=request.user).select_related('following')

    followers = [f.follower for f in followers_qs]
    following = [f.following for f in following_qs]

    return render(request, "accounts/followers_list.html", {
        "followers": followers,
        "following": following
    })

@login_required
def user_logout(request):
    # Accept POST only for logout to be secure
    if request.method == "POST":
        logout(request)
        messages.success(request, "✅ You have successfully logged out.")
        return redirect("accounts:login")
    # For any GET request, redirect somewhere safe (home)
    return redirect("home")
