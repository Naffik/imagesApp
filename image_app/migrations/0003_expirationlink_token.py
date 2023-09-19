# Generated by Django 4.2 on 2023-09-18 09:18

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('image_app', '0002_expirationlink'),
    ]

    operations = [
        migrations.AddField(
            model_name='expirationlink',
            name='token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
