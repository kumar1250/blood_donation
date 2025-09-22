

from django.db import models
from django.conf import settings
from django.utils import timezone

class BloodCamp(models.Model):
    name = models.CharField(max_length=200)
    organized_by = models.CharField(max_length=200)
    date = models.DateField()
    time = models.CharField(max_length=50)
    venue = models.TextField()
    city = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    min_age = models.IntegerField(default=18)
    max_age = models.IntegerField(default=60)
    min_weight = models.IntegerField(default=50)
    notes = models.TextField(blank=True, null=True)

    permanent = models.BooleanField(default=False)  # ✅ New field

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} at {self.venue}, {self.city}"

    def is_expired(self):
        if self.permanent:  # ✅ Never expire if permanent
            return False
        today = timezone.localdate()
        return self.date < today
 

