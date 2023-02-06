from django.http import HttpResponseNotFound
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, \
    permission_classes
from rest_framework.exceptions import NotFound, APIException
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.utils.encoding import escape_uri_path

from rest_framework.response import Response
from rest_framework.views import APIView

from v1.albums.models.album import Album
from v1.albums.serializers.album_detail import AlbumDetailSerializer
from v1.albums.serializers.album_list import (
    AlbumListSerializer
)
from v1.images.models.image import Image
from v1.images.serializers.image import ImageUploadSerializer


def get_album(user, path):
    """
    Selects `album` from database based on its `path` attribute.
    """

    path = f"{user.email}-{path}"
    album = get_object_or_404(user.albums.all(), path=escape_uri_path(path))

    return album


class AlbumListView(APIView):
    """
    List view for the album model.
    """
    permission_classes = (IsAuthenticated, )

    @staticmethod
    def get_queryset(request, qs):
        return qs.filter(user=request.user)

    @staticmethod
    def get(request):
        """
        List all users albums.

        :param request:
        :return: list of albums.
        """

        qs = AlbumListView.get_queryset(
            request,
            Album.objects.all()
        )
        serializer = AlbumListSerializer(qs, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request):
        """
        Create new album.
        :param request:
        :return: created album.
        """

        serializer = AlbumListSerializer(data=request.data,
                                         context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors.get('name')
        if len(errors) == 1 and errors[0].code == 'unique':
            return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AlbumDetailView(APIView):
    """
    API view to manipulate with specific album.
    """

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get(request, path):
        """
        Retrieve one album.
        :param request: GET
        :param path: Path to the album in storage.
        :return: Specific album with one photo to preview.
        """
        album = get_album(request.user, path)
        serializer = AlbumDetailSerializer(album)
        return Response(serializer.data)

    @staticmethod
    def delete(request, path):
        """
        Delete specific album.
        :param request: DELETE
        :param path: Path to the album in storage.
        :return: in success return 200 status code.
        """
        album = get_album(request.user, path)
        album.delete_album_directory()
        album.delete()
        return Response(None, status.HTTP_200_OK)

    @staticmethod
    def post(request, path):
        """
        Upload new photos to the specific album.
        :param request: POST
        :param path: Path to the album in storage.
        :return: Info about loaded images and info with errors.
        """
        success_response = {
            'uploaded': [],
            'errors': []
        }

        album = get_album(request.user, path)

        if not request.FILES:
            return Response({}, status.HTTP_400_BAD_REQUEST)

        try:
            for key, val in request.FILES.items():
                image = Image.create_from_file(album, val, request.user)
                serializer = ImageUploadSerializer(
                    data=image, context={'user': request.user}
                )
                if serializer.is_valid():
                    img = serializer.save()
                    success_response['uploaded'].append({
                        'name': img.name,
                        'path': img.path,
                        'fullpath': img.fullpath,
                        'modified': img.modified,
                    })
                else:
                    success_response['errors'].append({
                        'name': val.name,
                        'error': serializer.errors
                    })

            return Response(success_response, status=status.HTTP_200_OK)
        except Exception as e:
            raise APIException()