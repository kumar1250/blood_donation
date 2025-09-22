from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True, unique=False)

    blood_group = models.CharField(max_length=5)
    address = models.TextField()

    def __str__(self):
        return str(self.username) if self.username else str(self.phone)

# Follow system
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following_set', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')  # prevent duplicate follows

    def __str__(self):
        return f"{self.follower} → {self.following}"
