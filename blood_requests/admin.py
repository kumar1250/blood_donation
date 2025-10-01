from django.contrib import admin
from .models import BloodRequest, Notification, DonorLocation

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ["name", "blood_group", "emergency", "requester", "created_at", "otp_verified"]
    search_fields = ["name", "blood_group", "requester__username", "email"]

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "message", "created_at", "read"]

@admin.register(DonorLocation)
class DonorLocationAdmin(admin.ModelAdmin):
    list_display = ["donor", "blood_request", "lat", "lng", "updated_at"]
