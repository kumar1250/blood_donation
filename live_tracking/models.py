from django.db import models
from django.conf import settings

class LiveLocation(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="live_location"
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_sharing = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} Location"
