from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .album import get_album
from ...images.models.image import Image as ImageModel
from ...images.serializers.image import ImageSerializer


def get_image(user, album_path, img_path):
    """
    Function returns specific image of some album.
    If image doesn't exist it will return 404 response.
    :param user: User instance
    :param album_path: Albums' path.
    :param img_path: Images' path.
    :return: Image instance or raise 404 response.
    """

    album = get_album(user, album_path)
    img = get_object_or_404(
        album.image_set.all(), path=img_path
    )
    return img


class ImageDetailView(APIView):
    """
    API view to retrieving specific images.
    """
    permission_classes = (IsAuthenticated, )

    @staticmethod
    def get(request, album_path, img_path):
        """
        Retrieve specific image.
        User can't access to another album via the access policy.
        So if user will request some doesn't exist albums user
        will get 404 response.

        :param request: GET
        :param album_path: Albums' path.
        :param img_path: Images' path.
        :return: Image or 404 Response.
        """

        img = get_image(request.user, album_path, img_path)
        serializer = ImageSerializer(img)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, album_path, img_path):
        """
        Delete specific image.
        :param request: DELETE
        :param album_path: Albums' path.
        :param img_path: Images' path
        :return: Image or 404 Response.
        """

        img = get_image(request.user, album_path, img_path)
        img.delete_image_file()
        img.delete()
        return Response(None, status=status.HTTP_200_OK)
