from django.db import models
from django.conf import settings


class BloodRequest(models.Model):
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("O+", "O+"),
        ("O-", "O-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
    ]

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blood_requests"
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)

    address = models.TextField()
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    emergency = models.BooleanField(default=False)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ OTP fields
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    otp_verified = models.BooleanField(default=False)

    # ✅ Donors accepted for this request
    accepted_donors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="donated_requests"
    )

    # ✅ Requester live location (optional, for map)
    requester_lat = models.FloatField(null=True, blank=True)
    requester_lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.blood_group}) - {'Emergency' if self.emergency else 'Normal'}"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}"
