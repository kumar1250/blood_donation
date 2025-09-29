from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from blood_camp.models import BloodCamp
from blood_requests.models import BloodRequest


def home(request):
    """
    Home page view: shows upcoming camps and recent blood requests.
    """
    today = timezone.now().date()

    # Upcoming camps, ordered by date
    upcoming_camps = BloodCamp.objects.filter(date__gte=today).order_by("date")

    # Latest 5 blood requests
    recent_requests = BloodRequest.objects.order_by("-created_at")[:5]

    context = {
        "upcoming_camps": upcoming_camps,
        "recent_requests": recent_requests,
        "total_camps": BloodCamp.objects.count(),
        "upcoming_camps_count": upcoming_camps.count(),
        "total_requests": BloodRequest.objects.count(),
    }
    return render(request, "home/home.html", context)


@login_required
def dashboard(request):
    """
    Dashboard view: shows statistics and recent items for blood camps and requests.
    """
    today = timezone.now().date()

    # Optional: delete past camps (if you want to remove old ones)
    # BloodCamp.objects.filter(date__lt=today).delete()

    # Statistics
    total_camps = BloodCamp.objects.count()
    upcoming_camps = BloodCamp.objects.filter(date__gte=today).count()
    total_requests = BloodRequest.objects.count()

    # Recent items (last 5)
    recent_camps = BloodCamp.objects.order_by("-created_at")[:5]
    recent_requests = BloodRequest.objects.order_by("-created_at")[:5]

    context = {
        "total_camps": total_camps,
        "upcoming_camps": upcoming_camps,
        "total_requests": total_requests,
        "recent_camps": recent_camps,
        "recent_requests": recent_requests,
    }

    return render(request, "blood_camp/dashboard.html", context)
