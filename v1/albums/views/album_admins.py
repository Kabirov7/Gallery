from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from v1.albums.models.album import Album


class AlbumAdminsView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)

    @staticmethod
    def delete(request):
        qs = Album.objects.all().iterator()
        for album in qs:
            album.delete_album_directory()
            album.delete()
        return Response(None, status=status.HTTP_200_OK)

