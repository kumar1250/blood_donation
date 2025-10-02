from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import BloodCamp
from blood_requests.models import BloodRequest
from .forms import BloodCampForm  # ✅ use the form



@login_required
def create_camp(request):
    if request.method == "POST":
        form = BloodCampForm(request.POST)
        if form.is_valid():
            camp = form.save(commit=False)
            camp.organizer = request.user   # ✅ assign logged-in user
            camp.save()
            messages.success(request, "✅ Blood camp created successfully!")
            return redirect("blood_camp:camp_list")
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = BloodCampForm()

    return render(request, "blood_camp/create_camp.html", {"form": form})

<<<<<<< HEAD
=======
from django.utils import timezone
from datetime import timedelta
>>>>>>> 6942391 (Initial commit: Updated project with new files and blood camp changes blood camp)

@login_required
def camp_list(request):
    """
    List all upcoming blood camps and today's camps.
<<<<<<< HEAD
    Automatically deletes past camps.
    """
    # Delete all past camps
    BloodCamp.objects.filter(date__lt=timezone.now().date()).delete()
    
    # Fetch upcoming and today's camps, ordered by date
    camps = BloodCamp.objects.filter(date__gte=timezone.now().date()).order_by("date")
    
    return render(request, "blood_camp/camp_list.html", {"camps": camps})
@login_required
def dashboard(request):
    BloodCamp.objects.filter(date__lt=timezone.now().date()).delete()
    camps = BloodCamp.objects.all().order_by("date")
    requests = BloodRequest.objects.all().order_by("-created_at")
    return render(request, "blood_camp/dashboard.html", {"camps": camps, "requests": requests})


=======
    Automatically deletes camps older than yesterday.
    """
    # Delete camps older than yesterday
    yesterday = timezone.now().date() - timedelta(days=1)
    BloodCamp.objects.filter(date__lt=yesterday).delete()
    
    # Fetch upcoming and today's camps, ordered by date
    camps = BloodCamp.objects.filter(date__gte=yesterday).order_by("date")
    
    return render(request, "blood_camp/camp_list.html", {"camps": camps})

@login_required
def dashboard(request):
    # Delete camps older than yesterday
    yesterday = timezone.now().date() - timedelta(days=1)
    BloodCamp.objects.filter(date__lt=yesterday).delete()
    
    camps = BloodCamp.objects.filter(date__gte=yesterday).order_by("date")
    requests = BloodRequest.objects.all().order_by("-created_at")
    
    return render(request, "blood_camp/dashboard.html", {"camps": camps, "requests": requests})

>>>>>>> 6942391 (Initial commit: Updated project with new files and blood camp changes blood camp)
@login_required
def delete_camp(request, camp_id):
    camp = get_object_or_404(BloodCamp, id=camp_id)
    if request.user != camp.organizer:
        return HttpResponseForbidden("❌ You cannot delete this camp.")
    if request.method == "POST":
        camp.delete()
        messages.success(request, "✅ Camp deleted successfully.")
        return redirect("blood_camp:camp_list")
    return render(request, "blood_camp/confirm_delete.html", {"camp": camp})
