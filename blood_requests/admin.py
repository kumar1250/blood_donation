from django.contrib import admin
from .models import BloodRequest, Notification, DonorLocation

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "emergency", "created_at")
    list_filter = ("emergency", "created_at")
    search_fields = ("name", "email", "phone")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "read", "created_at")
    list_filter = ("read", "created_at")
    search_fields = ("user__username", "message")

@admin.register(DonorLocation)
class DonorLocationAdmin(admin.ModelAdmin):
    list_display = ("donor", "blood_request", "lat", "lng", "updated_at")
    list_filter = ("blood_request", "updated_at")
    search_fields = ("donor__username",)
