from rest_framework import serializers

from ..models.image import Image
from ...albums.models.album import Album


class ImageSerializer(serializers.ModelSerializer):
    """
    REST API serializer for the Image model.
    """
    class Meta:
        model = Image
        fields = ['path', 'fullpath', 'name', 'modified']


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['album', 'path', 'fullpath', 'name', 'file']


class ImagePreviewSerializer(serializers.Serializer):
    x_size = serializers.IntegerField(min_value=0)
    y_size = serializers.IntegerField(min_value=0)

    def validate(self, data):
        if data['x_size'] + data['y_size'] == 0:
            raise serializers.ValidationError('Both sizes can\'t be zero!')

        return data
