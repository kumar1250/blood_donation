# blood_requests/admin.py
from django.contrib import admin
from .models import BloodRequest   # ✅ same name as models.py

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "emergency", "created_at")
    list_filter = ("emergency", "created_at")
    search_fields = ("name", "email", "phone")
