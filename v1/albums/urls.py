from django.urls import path

from .views.album import AlbumListView, AlbumDetailView
from .views.album_admins import AlbumAdminsView
from .views.image import ImageDetailView

urlpatterns = [
    path('', AlbumListView.as_view(), name='album'),
    path('<str:path>', AlbumDetailView.as_view(),
         name='album-detail'),
    path('<str:album_path>/<str:img_path>', ImageDetailView.as_view(),
         name='album-img-detail'),
    path('delete_all/', AlbumAdminsView.as_view(), name='albums-delete-all'),
]
