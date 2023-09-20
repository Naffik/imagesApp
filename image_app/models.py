import uuid

from django.db import models
from django.utils import timezone

from user_app.models import User


class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', null=True)
    original_image = models.ImageField(upload_to='images/original/')


class Thumbnail(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='thumbnails', null=False)
    thumbnail = models.ImageField(upload_to='images/thumbnails/')


class ExpirationLink(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='img')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    expiration_time = models.DateTimeField()

    def is_valid(self):
        return self.expiration_time > timezone.now()
