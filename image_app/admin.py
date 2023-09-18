from django.contrib import admin
from image_app.models import Image, Thumbnail, ExpirationLink

admin.site.register(Image)
admin.site.register(Thumbnail)
admin.site.register(ExpirationLink)
