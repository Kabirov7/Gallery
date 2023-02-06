import logging
import os
import shutil
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import get_storage_class
from django.db import models
from django.utils.translation import gettext as _
from django.utils.encoding import escape_uri_path
from PIL import Image as PILImage
import time

from v1.albums.models.album import Album

logger = logging.getLogger(__name__)
storage = get_storage_class()()


def image_directory_path(instance, filename):
    """
    Helper function that returns full directory where the images are uploaded.
    It is composed by main album subdirectory, album name subdirectory
    and the image file name.
    """
    return '{}/{}/{}'.format('albums', instance.album.path, filename)


class Image(models.Model):
    album = models.ForeignKey(
        Album,
        related_name='image_set',
        help_text=_('Image belongs to album.'),
        on_delete=models.CASCADE,
    )

    file = models.ImageField(
        _('Image file'),
        max_length=1024,
        upload_to=image_directory_path,
        height_field='height',
        width_field='width',
        help_text=_('Representation of image in filesystem.')
    )

    height = models.PositiveSmallIntegerField(
        _('Image height'),
        null=True,
        blank=True,
        help_text=_('Image height. It will be populated automatically.')
    )

    width = models.PositiveSmallIntegerField(
        _('Image width'),
        null=True,
        blank=True,
        help_text=_('Image width. It will be populated automatically.')
    )

    path = models.CharField(
        _('Path'),
        max_length=1024,
        null=True,
        blank=True,
        help_text=_('Name of the image file (e.g. elephant.jpg).'),
    )

    fullpath = models.CharField(
        _('Full path'),
        max_length=1024,
        null=True,
        blank=True,
        unique=True,
        help_text=_(
            'Full path is composed from album `name` and image path.'),
    )

    name = models.CharField(
        _('Name'),
        max_length=1024,
        null=True,
        blank=True,
        help_text=_('Name of the image. It is generated from filename.'),
    )

    created = models.DateTimeField(
        _('Created'),
        auto_now_add=True,
        help_text=_('Timestamp of creation.'),
    )

    modified = models.DateTimeField(
        _('Modified'),
        auto_now=True,
        help_text=_('Timestamp of last modification.'),
    )

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    def __str__(self):
        return self.name or _('This image has no name')

    @property
    def fullpath(self):
        """
        Fullpath of the image for access image detail in URL.  It is composed
        by album path and the image filename.
        """
        return '{}/{}'.format(Album.get_folder_name(self.album.path),
                              self.path)

    @staticmethod
    def create_from_file(album, file, user):
        """
        Cretes `Image` instance from the file (Django `File` object). Parses
        and generates `name` and assigns image to album.
        """
        filename, extension = os.path.splitext(file.name)

        # path composed from name, user ID, time(ms) and extension
        new_filename = '{filename}-{user_id}_{time}{extension}'.format(
            filename=filename,
            user_id=user.id,
            extension=extension,
            time=round(time.time()*1000)
        )

        # change also filename of file object itself
        file.name = new_filename

        nice_image_name = filename.capitalize()

        image = {
            'album': album.pk,
            'path': new_filename,
            'name': nice_image_name,
            'file': file,
        }
        return image

    @staticmethod
    def get_image_name(filename, fb_user_id):
        """
        Returns file name composed from original file name and
        id of the facebook user
        """
        filename, extension = os.path.splitext(filename)
        return '{filename}-{fb_user_id}{extension}'.format(
            filename=filename,
            fb_user_id=fb_user_id,
            extension=extension)

    def _get_image_directory(self):
        """
        Returns directory, where the image is stored. It is relative path to
        `MEDIA_ROOT`.
        """
        return os.path.dirname(self.file.name)

    def delete_image_file(self):
        """
        Deletes image file with all its thumbnails.
        """
        # delete image file
        storage.delete(self.file.name)