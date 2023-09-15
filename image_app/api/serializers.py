from rest_framework import serializers
from image_app.models import Image, Thumbnail
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
        print(image_extension)
        if image_extension == '.jpg':
            image_extension = '.jpeg'
        print(image_extension)
        image_obj = Image.objects.create(**validated_data)
        user = validated_data.get('user')
        thumbnail_sizes = list(map(int, user.account_tier.thumbnail_size.split(',')))
        with img.open(image) as im:
            for size in thumbnail_sizes:
                thumbnail_name = f"{image_name}_thumbnail_{size}{image_extension}"
                im.thumbnail((size, size))
                buffer = BytesIO()
                im.save(buffer, image_extension.replace('.', ''))
                thumbnail_obj = Thumbnail.objects.create(name=thumbnail_name, image=image_obj)
                thumbnail_obj.thumbnail.save(thumbnail_name, buffer)
                print(thumbnail_obj)
        return image_obj

    def get_fields(self):
        fields = super().get_fields()
        user = self.context['request'].user
        if not user.account_tier.original_link:
            fields.pop('original_image')
        return fields
