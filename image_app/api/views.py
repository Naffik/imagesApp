import magic

from datetime import timedelta

from django.http import FileResponse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .pagination import ImagePagination
from .serializers import ImageSerializer, ExpirationLinkSerializer
from image_app.models import Image, ExpirationLink

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'JPG']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class CreateImageView(generics.CreateAPIView):
    """
    Create a new image with POST data.

    Parameters:
    - original_image: The image file to be uploaded. The file should have a supported extension.
    """
    queryset = Image.objects.all()
    permissions_classes = [IsAuthenticated]
    serializer_class = ImageSerializer
    throttle_scope = 'image_upload'

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        if 'original_image' not in request.FILES:
            raise ValidationError('File not uploaded')
        file = request.FILES['original_image']
        try:
            if not allowed_file(file.name):
                raise ValidationError('File extension not allowed')
        except DjangoValidationError:
            raise ValidationError('Incorrect file')
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class ListImageView(generics.ListAPIView):
    """
    List all images associated with the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer
    pagination_class = ImagePagination
    throttle_scope = 'images_list'

    def get_queryset(self):
        user = self.request.user
        return Image.objects.all().filter(user=user)


class ExpirationLinkCreateAPIView(APIView):
    """
    Create an expiration link for a specified image using POST data.

    Parameters:
    - id: The unique identifier of the image.

    """
    throttle_scope = 'create_link'

    def post(self, request, pk):
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            image = Image.objects.get(pk=pk)
        except Image.DoesNotExist:
            return Response({'error': 'Photo not found'}, status=status.HTTP_404_NOT_FOUND)

        if image.user != request.user:
            return Response({'error': 'You do not have permission to create an expiration link for this photo'},
                            status=status.HTTP_403_FORBIDDEN)

        min_duration = user.account_tier.expiring_link_duration_min
        max_duration = user.account_tier.expiring_link_duration_max
        expiration_time = request.data.get('expiration-time', None)

        if not expiration_time:
            return Response({'error': 'Expiration time not specified'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            expiration_time = int(request.data.get('expiration-time', None))
            if not min_duration <= expiration_time <= max_duration:
                raise ValueError
        except (ValueError, TypeError):
            return Response({'error': f'Expiration time needs to be between {min_duration} and {max_duration}'},
                            status=status.HTTP_400_BAD_REQUEST)

        expiration_time = timezone.now() + timedelta(seconds=int(expiration_time))

        link = ExpirationLink(image=image, expiration_time=expiration_time)
        link.save()

        serializer = ExpirationLinkSerializer(link, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExpirationLinkRetrieveView(APIView):
    """
    Retrieve an image associated with a given expiration link.

    Parameters:
    - token: The unique identifier associated with the ExpirationLink.

    """
    throttle_scope = 'expiring_images'

    def get(self, request, token):
        try:
            exp_link = ExpirationLink.objects.get(token=token)
        except ExpirationLink.DoesNotExist:
            return Response({'error': 'Invalid or expired link'}, status=status.HTTP_404_NOT_FOUND)

        if not exp_link.is_valid():
            return Response({'error': 'Link has expired'}, status=status.HTTP_410_GONE)

        image_path = exp_link.image.original_image.path
        image_content_type = magic.from_file(image_path, mime=True)
        img = open(image_path, 'rb')
        return FileResponse(img, content_type=image_content_type)
