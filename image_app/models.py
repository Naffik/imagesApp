from django.db import models
from user_app.models import User


class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', null=True)
    original_image = models.ImageField(upload_to='images/original/')


class Thumbnail(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='thumbnails', null=False)
    thumbnail = models.ImageField(upload_to='images/thumbnails/')
