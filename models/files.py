# yacon.models.files.py
import os, logging, json, urllib

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from yacon import conf
from yacon.models.common import TimeTrackedModel

logger = logging.getLogger(__name__)

# ============================================================================
# File Management Classes

class FileSpec(object):
    def __init__(self, node, prefix=None, node_is_file=False):
        self.node = node
        self.prefix = prefix
        self.node_is_file = node_is_file
        self.basename = None
        self.relative_filename = None
        self._parse_node()

    def _parse_node(self):
        pieces = self.node.split(':')
        try:
            self.file_type = pieces[0]
            x = urllib.unquote(pieces[1])
            if self.node_is_file:
                self.relative_dir = os.path.dirname(x)
            else:
                self.relative_dir = x

            if self.prefix:
                self.relative_dir = os.path.join(self.prefix, self.relative_dir)

            if self.file_type == 'public':
                self.full_dir = os.path.join(settings.MEDIA_ROOT,
                    self.relative_dir)
            elif self.file_type == 'private' and conf.site.private_upload:
                self.full_dir = os.path.join(conf.site.private_upload, 
                    self.relative_dir)
            elif self.file_type == 'system':
                # special case for creating root level folders in the admin
                if self.relative_dir == 'public':
                    self.full_dir = settings.MEDIA_ROOT
                elif self.relative_dir == 'private':
                    self.full_dir = conf.site.private_upload
                else:
                    raise Http404('bad path for system type')
            else:
                raise Http404('bad tree type')

            if self.node_is_file:
                self.set_filename(os.path.basename(x))
        except IndexError:
            raise Http404('bad node key')

    def set_filename(self, filename):
        self.basename = filename
        self.relative_filename = os.path.join(self.relative_dir, filename)
        self.full_filename = os.path.join(self.full_dir, self.basename)
        if os.path.isdir(self.full_filename):
            self.node_is_file = False
        else:
            self.node_is_file = True

    @property
    def is_private(self):
        return self.file_type == 'private'

    @property
    def title(self):
        if self.basename:
            return self.basename

        return os.path.basename(self.relative_dir)

    @property
    def results(self):
        return {
            'success':True,
            'filename':self.relative_filename,
        }

    @property
    def json_results(self):
        return json.dumps(self.results)

    @property
    def key(self):
        if self.relative_filename:
            return '%s:%s' % (self.file_type, self.relative_filename)

        return '%s:%s' % (self.file_type, self.relative_dir)

# ============================================================================
# Handler Objects

class GeneralHandler(object):
    handler_type = 'gen'


class FolderHandler(object):
    handler_type = 'fld'


class ImageHandler(object):
    handler_type = 'img'

# ============================================================================
# Django Models

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
    owner = models.ForeignKey(User, null=True, blank=True)

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

    @classmethod
    def create_from_spec(cls, spec, owner=None):
        """Creates a StoredFile object based on an existing file denoted by a
        FileSpec object."""
        files = StoredFile.objects.filter(owner=owner, 
            file_field=spec.relative_filename, is_private=spec.is_private)
        if files:
            spec.stored = files[0]
        else:
            spec.stored = StoredFile.objects.create(owner=owner,
                file_field=spec.relative_filename, is_private=spec.is_private)
        return spec.stored

    @property
    def url(self):
        # ??? need to add code for private urls

        return self.file_field.url


class FileGrouping(TimeTrackedModel):
    files = models.ManyToManyField(StoredFile)
