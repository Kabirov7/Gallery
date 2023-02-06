from rest_framework import serializers

from v1.albums.models.album import Album
from v1.images.serializers.image import ImageSerializer


class AlbumDetailSerializer(serializers.ModelSerializer):
    """
    REST API detail serializer show all images of the album.
    """
    images = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = ['path', 'name', 'images']

    def get_images(self, obj):
        image = obj.image_set.all()
        serializer = ImageSerializer(image, many=True)
        return serializer.data

    def get_path(self, obj):
        return Album.get_folder_name(obj.path)
