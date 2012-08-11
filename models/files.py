# yacon.models.files.py
import logging

from django.contrib.auth.models import User
from django.db import models

from yacon.models.common import TimeTrackedModel

logger = logging.getLogger(__name__)

# ============================================================================

class GeneralHandler(object):
    handler_type = 'gen'


class FolderHandler(object):
    handler_type = 'fld'


class ImageHandler(object):
    handler_type = 'img'


class StoredFile(TimeTrackedModel):
    HANDLERS = (
        (FolderHandler.handler_type, FolderHandler),
        (GeneralHandler.handler_type, GeneralHandler),
        (ImageHandler.handler_type, ImageHandler),
    )
    HANDLERS_DICT = dict(HANDLERS)

    is_private = models.BooleanField(default=False)
    #handler = models.CharField(choices=HANDLERS_DICT)
    #file_field = models.FileField(upload_to=File.content_file_name)
    file_field = models.FileField(upload_to='files')
    owner = models.ForeignKey(User)

    def __unicode__(self):
        prefix = 'public'
        if self.is_private:
            prefix = 'private'
        return '%s:%s' % (prefix, self.file_field)

    @classmethod
    def content_file_name(cls, instance, filename):
        """Callable for determining the upload_to field for the file_field
        attribute of an instnace of this class.  Changes where the upload_to
        directory is based on whether or not the object is public or private.
        """
        upload_to = 'public/'
        if instance.is_private:
            upload_to = 'private/'

        return upload_to + filename


class FileGrouping(TimeTrackedModel):
    files = models.ManyToManyField(StoredFile)
