from django.urls import reverse
from rest_framework import serializers
from image_app.models import Image, Thumbnail, ExpirationLink
from PIL import Image as img
import os
from io import BytesIO


class ThumbnailSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(use_url=True)

    class Meta:
        model = Thumbnail
        fields = ['id', 'name', 'thumbnail']


class ImageSerializer(serializers.ModelSerializer):
    thumbnails = ThumbnailSerializer(many=True, read_only=True)
    original_image = serializers.ImageField(use_url=True)

    class Meta:
        model = Image
        fields = ['id', 'original_image', 'thumbnails']

    def create(self, validated_data):
        image = validated_data['original_image']
        image_name, image_extension = os.path.splitext(image.name)
        if image_extension == '.jpg':
            image_extension = '.jpeg'
        image_obj = Image.objects.create(**validated_data)
        user = validated_data.get('user')
        thumbnail_sizes = list(map(int, user.account_tier.thumbnail_size.split(',')))
        with img.open(image) as im:
            original_width, original_height = im.size
            for height in thumbnail_sizes:
                thumbnail_name = f"{image_name}_thumbnail_{height}{image_extension}"
                aspect_ratio = original_width / original_height
                new_width = int(aspect_ratio * height)
                im.thumbnail((height, new_width))
                buffer = BytesIO()
                if image_extension == '.jpeg':
                    im.save(buffer, format='JPEG', quality=85)
                else:
                    im.save(buffer, image_extension.replace('.', ''))
                thumbnail_obj = Thumbnail.objects.create(name=thumbnail_name, image=image_obj)
                thumbnail_obj.thumbnail.save(thumbnail_name, buffer)
        return image_obj

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context['request'].user
        if not user.account_tier.original_link:
            representation.pop('original_image', None)
        return representation


class ExpirationLinkSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField()
    expiration_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ExpirationLink
        fields = ('expiration_time', 'link',)

    def get_image(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.image.original_image.url)
        return obj.image.original_image.url

    def get_link(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('retrieve_expiring_image', kwargs={'token': obj.token}))
