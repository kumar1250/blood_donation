from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import BloodCamp
from blood_requests.models import BloodRequest
from .forms import BloodCampForm
from blood_camp.models import BloodCamp

from datetime import datetime
from django.db.models import Q

from django.contrib import messages
from .models import BloodCamp

@login_required
def dashboard(request):
    all_camps = BloodCamp.objects.all()
    upcoming_camps_qs = BloodCamp.objects.filter(date__gte=timezone.localdate()).order_by("date")
    all_requests = BloodRequest.objects.all()

    context = {
        "total_camps": all_camps.count(),
        "upcoming_camps": upcoming_camps_qs.count(),
        "total_requests": all_requests.count(),
        "recent_camps": all_camps.order_by("-date")[:5],
        "recent_requests": all_requests.order_by("-created_at")[:5],
    }
    return render(request, "blood_camp/dashboard.html", context)





def camp_list(request):
    city = request.GET.get("city", "")
    today = timezone.localdate()
    now_time = timezone.localtime().time()

    # Delete expired camps (only non-permanent)
    expired_camps = BloodCamp.objects.filter(
        Q(permanent=False),
        Q(date__lt=today) | Q(date=today, time__lt=now_time)
    )
    expired_camps.delete()

    # Remaining camps: future or permanent
    camps = BloodCamp.objects.filter(
        Q(permanent=True) | 
        Q(date__gt=today) |  
        Q(date=today, time__gte=now_time) |
        Q(date__isnull=True) | Q(time__isnull=True)
    ).order_by("date")

    if city:
        camps = camps.filter(city__icontains=city)

    return render(request, "blood_camp/camp_list.html", {"camps": camps, "city": city})

@login_required
def camp_detail(request, camp_id):
    camp = get_object_or_404(BloodCamp, id=camp_id)
    
    if not camp.permanent and camp.date < timezone.localdate():
        messages.warning(request, "⚠️ This blood camp has already passed.")
    
    return render(request, "blood_camp/camp_detail.html", {"camp": camp})

@login_required
def create_camp(request):
    if request.method == "POST":
        form = BloodCampForm(request.POST)
        if form.is_valid():
            camp = form.save(commit=False)
            camp.created_by = request.user
            camp.save()
            messages.success(request, "✅ Blood camp created successfully!")
            return redirect("blood_camp:camp_list")
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = BloodCampForm()

    return render(request, "blood_camp/create_camp.html", {"form": form})
