from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CreateImageView, ListImageView

router = DefaultRouter()

urlpatterns = [
    path(r'upload/', CreateImageView.as_view(), name='image_create'),
    path(r'list/', ListImageView.as_view(), name='image_list'),
]
