from django.db import models
from django.conf import settings

# -------------------
# Blood Request Model
# -------------------
class BloodRequest(models.Model):
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"), ("A-", "A-"), ("B+", "B+"), ("B-", "B-"),
        ("O+", "O+"), ("O-", "O-"), ("AB+", "AB+"), ("AB-", "AB-"),
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

    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    otp_verified = models.BooleanField(default=False)

    accepted_donors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="donated_requests"
    )

    requester_lat = models.FloatField(null=True, blank=True)
    requester_lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.blood_group}) - {'Emergency' if self.emergency else 'Normal'}"

# -------------------
# Notifications
# -------------------
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

# -------------------
# Donor Location per Blood Request
# -------------------
class DonorLocation(models.Model):
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="donor_locations"
    )
    blood_request = models.ForeignKey(
        BloodRequest,
        on_delete=models.CASCADE,
        related_name="donor_locations"
    )
    lat = models.FloatField()
    lng = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("donor", "blood_request")

    def __str__(self):
        return f"{self.donor.username} → {self.blood_request.name} ({self.lat}, {self.lng})"
