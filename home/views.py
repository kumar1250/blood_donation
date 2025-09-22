from django.shortcuts import render
from blood_camp.models import BloodCamp
from blood_requests.models import BloodRequest
from django.utils import timezone

def home(request):
    # All upcoming camps, ordered by date
    upcoming_camps_qs = BloodCamp.objects.filter(date__gte=timezone.localdate()).order_by("date")

    # Latest 5 blood requests
    recent_requests_qs = BloodRequest.objects.all().order_by("-created_at")[:5]

    # Counts for dashboard stats
    upcoming_camps_count = upcoming_camps_qs.count()
    recent_requests_count = BloodRequest.objects.count()

    context = {
        "upcoming_camps": upcoming_camps_qs,
        "recent_requests": recent_requests_qs,
        "upcoming_camps_count": upcoming_camps_count,
        "recent_requests_count": recent_requests_count,
    }

    return render(request, "home/home.html", context)
