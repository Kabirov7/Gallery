import os
import shutil

from django.conf import settings
from django.core.files.storage import get_storage_class
from django.db import models
from django.utils.encoding import escape_uri_path
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from v1.accounts.models.user import User

storage = get_storage_class()()


def validate_album_name(value):
    """
    Validator fot the `Album.name` field. It can't contain '/' character.
    """
    if value and value.find('/') > -1:
        raise ValidationError(_('Album name can\'t contain \'/\' character'))


class Album(models.Model):
    """
    Album model represents some collection of users photos.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='albums',
        help_text=_('Owner of the album.')

    )

    name = models.CharField(
        max_length=1024,
        help_text=_('Name of the album. Must be unique.'),
        validators=[validate_album_name],
    )
    path = models.TextField(blank=False, null=False)

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Timestamp of creation.'),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('Timestamp of last modification.'),
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('user', 'name')

    def delete_album_directory(self):
        """
        Deletes album directory recursively with all the images and
        thumbnails.
        """

        # absolute path to album directory
        absolute_path = os.path.join(storage.location,
                                     'albums',
                                     self.path)

        try:
            # detele recursively
            shutil.rmtree(absolute_path)
        except Exception:
            pass

    @staticmethod
    def get_path(user, path):
        return escape_uri_path(f"{user.email}-{path}")

    @staticmethod
    def get_folder_name(path):
        return path.split('-',1)[1]



