from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail
import random

from django.contrib.auth import get_user_model
from .models import Follow
from .forms import RegisterForm

User = get_user_model()

# -------------------------------
# Registration
# -------------------------------
def signup(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "✅ Registration successful! Please login.")
            return redirect('login')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'accounts/signup.html', {'form': form})

# -------------------------------
# Login
# -------------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"✅ Welcome {user.username}!")
            return redirect("home")
        else:
            messages.error(request, "❌ Invalid username or password")
            return render(request, "accounts/login.html", {"username": username})
    return render(request, "accounts/login.html")

# -------------------------------
# OTP Utilities
# -------------------------------
def send_otp(email):
    otp = str(random.randint(1000, 9999))
    cache.set(email, otp, timeout=300)
    send_mail(
        "Your OTP Code",
        f"Your OTP is {otp}. Expires in 5 min.",
        "yourgmail@gmail.com",
        [email]
    )

# -------------------------------
# Forgot / Verify / Reset Password
# -------------------------------
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            send_otp(email)
            request.session["email"] = email
            messages.info(request, "✅ OTP sent to your email.")
            return redirect("verify_otp")
        else:
            messages.error(request, "❌ Email not registered")
    return render(request, "accounts/forgot_password.html")

def verify_otp(request):
    email = request.session.get("email")
    if not email:
        messages.error(request, "❌ Session expired")
        return redirect("forgot_password")
    if request.method == "POST":
        otp = request.POST.get("otp")
        cached_otp = cache.get(email)
        if cached_otp == otp:
            messages.success(request, "✅ OTP verified")
            return redirect("reset_password")
        else:
            messages.error(request, "❌ Invalid OTP")
    return render(request, "accounts/verify_otp.html")

def reset_password(request):
    email = request.session.get("email")
    if not email:
        messages.error(request, "❌ Session expired")
        return redirect("forgot_password")
    if request.method == "POST":
        new_password = request.POST.get("password")
        user = User.objects.filter(email=email).first()
        if user:
            user.password = make_password(new_password)
            user.save()
            messages.success(request, "✅ Password updated. Login again.")
            request.session.pop("email", None)
            return redirect("login")
        else:
            messages.error(request, "❌ Something went wrong. Try again.")
            return redirect("forgot_password")
    return render(request, "accounts/reset_password.html")

# -------------------------------
# Home Page
# -------------------------------
@login_required
def home(request):
    return render(request, "home.html")

# -------------------------------
# Follow / Unfollow Users
# -------------------------------
@login_required
def follow_user(request, username):
    other_user = User.objects.filter(username=username).first()
    if other_user and other_user != request.user:
        Follow.objects.get_or_create(follower=request.user, following=other_user)
    return redirect("home")

@login_required
def unfollow_user(request, username):
    other_user = User.objects.filter(username=username).first()
    if other_user:
        Follow.objects.filter(follower=request.user, following=other_user).delete()
    return redirect("home")

# -------------------------------
# Followers & Following List
# -------------------------------
@login_required
def followers_list(request):
    followers = Follow.objects.filter(following=request.user)
    following = Follow.objects.filter(follower=request.user)
    return render(request, "accounts/followers_list.html", {
        "followers": followers,
        "following": following
    })
