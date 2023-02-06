from django.utils.encoding import escape_uri_path
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from v1.albums.models.album import Album, validate_album_name
from v1.images.serializers.image import ImageSerializer


class AlbumListSerializer(serializers.ModelSerializer):
    """
    REST API serializer for the Album model.
    Show one image of the album collection.
    """
    image = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Album
        fields = ['path', 'name', 'image']

    def get_image(self, obj):
        result = None
        image = obj.image_set.all().first()
        if image:
            serializer = ImageSerializer(image)
            result = serializer.data
        return result

    def get_path(self, obj):
        return Album.get_folder_name(obj.path)

    def create(self, validated_data):
        user = self.context['user']
        path = Album.get_path(user, validated_data['name'])
        album = Album.objects.create(
            user=user,
            name=validated_data['name'],
            path=path
        )
        return album

    def _remove_image_from_fields(self, repre):
        if repre['image'] is None:
            repre.pop('image')

    def to_representation(self, obj):
        result = super(AlbumListSerializer, self).to_representation(obj)
        self._remove_image_from_fields(result)
        return result

    def is_valid(self, raise_exception=False):
        result = super(AlbumListSerializer, self).is_valid(
            raise_exception=raise_exception)
        return result

    def validate_name(self, val):
        if bool(self.context['user'].albums.filter(name=val)):
            raise ValidationError(f'Name \'{val}\' is already taken.')
        validate_album_name(val)
        return val