from django.db import models
from django.contrib.auth.models import User

class UserMetadata(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interests = models.CharField(max_length=50, blank=True, null=True)  # free text, no choices
    drives = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)  # <-- new bio field

    def __str__(self):
        return self.user.username