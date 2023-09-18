from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreateImageView, ListImageView, ExpirationLinkCreateAPIView, ExpirationLinkRetrieveView

router = DefaultRouter()

urlpatterns = [
    path('upload/', CreateImageView.as_view(), name='image_create'),
    path('list/', ListImageView.as_view(), name='image_list'),
    path('create-link/<int:pk>/', ExpirationLinkCreateAPIView.as_view(), name='create_expiring_link'),
    path('expiring-images/<uuid:token>/', ExpirationLinkRetrieveView.as_view(), name='retrieve_expiring_image'),
]
