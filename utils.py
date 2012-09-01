# yacon.utils.py
import logging, json, inspect, urllib, os

from django.conf import settings
from django.http import HttpResponse

from yacon import conf

logger = logging.getLogger(__name__)

# ============================================================================
# Utility Classes
# ============================================================================

# Enum
#
# borrowed and modified from:
#  http://tomforb.es
#      /using-python-metaclasses-to-make-awesome-django-model-field-choices

class Enum(object):
    """A tuple of tuples pattern of (id, string) is common in django for
    choices fields, etc.  This object inspects its own members (i.e. the
    inheritors) and produces the corresponding tuples.

    Example:

    class Colours(Enum):
        RED = 'r'
        BLUE = 'b', 'Blueish'

    >> Colours.RED
    'r'
    >> list(Colours)
    [('r', 'Red'), ('b', 'Blueish')]
    """
    class __metaclass__(type):
        def __init__(self, *args, **kwargs):
            self._data = []
            for name, value in inspect.getmembers(self):
                if not name.startswith('_') and not inspect.ismethod(value):
                    if isinstance(value, tuple) and len(value) > 1:
                        data = value
                    else:
                        pieces = [x.capitalize() for x in name.split('_')]
                        data = (value, ' '.join(pieces))
                    self._data.append(data)
                    setattr(self, name, data[0])

            self._hash = dict(self._data)

        def __iter__(self):
            for value, data in self._data:
                yield (value, data)

    @classmethod
    def get_value(self, key):
        return self._hash[key]


class JSONResponse(HttpResponse):
    def __init__(self, obj, **kwargs):
        extra_headers = kwargs.pop('extra_headers', {})
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(json.dumps(obj), **kwargs)

        for key, value in extra_headers.items():
            self[key] = value

# ============================================================================
# File Browser Tools
# ============================================================================

class FileSpec(object):
    """Abstracts concept of public and private files and where they are served
    from."""
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

    def allowed_for_user(self, user):
        if user.is_superuser:
            return True

        # user is normal user, verify spec against the user's username
        name = 'users/%s/' % user.username
        if self.relative_dir.startswith(name):
            return True

        return False

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


# -------------------
# Dynatree Methods

def files_subtree(spec, depth_limit, expanded):
    """Returns a hash representation in dynatree format of the public or
    private upload directories."""
    file_hash = {
        'title':spec.title,
        'key':spec.key,
        'icon':'fatcow/folder.png',
        'isLazy':True,
    }

    if depth_limit == 0 and file_hash['key'] not in expanded:
        # reached as far as we're going to go, check for kids
        has_child_directories = False
        for x in os.listdir(spec.full_dir):
            if os.path.isdir(x):
                has_child_directories = True
                break

        if has_child_directories:
            file_hash['isLazy'] = True

        return file_hash

    # process any child directories
    children = []
    for x in os.listdir(spec.full_dir):
        dir_path = os.path.abspath(os.path.join(spec.full_dir, x))
        if os.path.isdir(dir_path):
            dl = depth_limit
            if dl != -1:
                dl = dl - 1

            # if the file_type is system, then convert to what is under it
            # (either public or private), otherwise just add to the parent's
            # key
            if spec.file_type != 'system':
                key = '%s:%s' % (spec.file_type, os.path.join(
                    spec.relative_dir, x))
            else:
                key = '%s:%s' % (spec.basename, x)

            spec2 = FileSpec(key)
            subtree = files_subtree(spec2, dl, expanded)
            children.append(subtree)

    if children:
        file_hash['children'] = children

    return file_hash


def build_filetree(expanded, restricted=None):
    """Returns a dynatree hash representation of our public and private file
    directory hierarchy."""
    spec = FileSpec('system:public')
    spec.set_filename('public')
    public_node = {
        'title': 'Public',
        'key': 'system:public',
        'expand': True,
        'icon': 'fatcow/folders_explorer.png',
    }
    if restricted:
        # restricted to a single user's folders
        spec = FileSpec('public:users/%s' % restricted)
        public_node['children'] = {
            'title': restricted,
            'key': 'public:users/%s' % restricted,
            'isLazy': True,
            'icon':'fatcow/folder.png',
        }
    else:
        public = files_subtree(spec, 2, expanded)
        if 'children' in public:
            public_node['children'] = public['children']
            public['children'][0]['activate'] = True

    spec = FileSpec('system:private')
    spec.set_filename('private')
    private_node = {
        'title': 'Private',
        'key': 'system:private',
        'expand': True,
        'icon': 'fatcow/folders_explorer.png',
    }

    if restricted:
        # restricted to a single user's folders
        spec = FileSpec('private:users/%s' % restricted)
        private_node['children'] = {
            'title': restricted,
            'key': 'private:users/%s' % restricted,
            'isLazy': True,
            'icon':'fatcow/folder.png',
        }
    else:
        private = files_subtree(spec, 2, expanded)
        if 'children' in private:
            private_node['children'] = private['children']
            private['children'][0]['activate'] = True

    tree = [public_node, private_node]
    return tree

# ============================================================================
# Miscellaneous Methods
# ============================================================================

# get_user_attributes
# 
# borrowed and modified from: 
#   http://stackoverflow.com/questions/4241171/inspect-python-class-attributes

def get_user_attributes(obj, exclude_methods=True):
    """Returns a list of non-system attributes for an object.

    :param obj: object or class to inspect
    :param exclude_methods: [optional] do not include callable methods in the
        returned list, defaults to True
    
    :returns: list of non-system attributes of an object or class
    """
    base_attributes = dir(type('dummy', (object,), {}))
    attributes = dir(obj)
    results = []
    for attribute in attributes:
        try:
            if attribute in base_attributes \
                    or (exclude_methods and callable(getattr(obj, attribute))):
                continue
            results.append(attribute)
        except AttributeError:
            # some kinds of access cause problems, ignore them
            pass

    return results


