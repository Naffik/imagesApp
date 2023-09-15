from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from user_app.api.managers import CustomUserManager


# Dopisać walidację thumbnail_size czy admin wpisał liczby po przecinku jakieś wyrażenie regularne
class AccountTier(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    thumbnail_size = models.CharField(max_length=255, null=False, blank=False)
    original_link = models.BooleanField(default=False)
    expiring_link = models.BooleanField(default=False)
    expiring_link_duration_min = models.IntegerField(default=300)
    expiring_link_duration_max = models.IntegerField(default=30000)

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=32, null=True, blank=True)
    last_name = models.CharField(max_length=32, null=True, blank=True)
    account_tier = models.ForeignKey(AccountTier, on_delete=models.CASCADE, null=True, blank=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username
