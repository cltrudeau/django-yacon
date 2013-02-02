# yacon.utils.py
import logging, json, inspect, urllib, os, locale, re
from itertools import islice, chain
from PIL import Image

from django.conf import settings
from django.http import HttpResponse, Http404

from yacon import conf
from yacon.models.hierarchy import NodeTranslation
from yacon.models.pages import PageType, BlockType

logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, '')

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


# QuerySetChain
#
# borrowed and modified from:
#   http://stackoverflow.com/questions/431628/
#   by: http://stackoverflow.com/users/15770/akaihola
class QuerySetChain(object):
    """
    Chains multiple subquerysets (possibly of different models) and behaves as
    one queryset.  Supports minimal methods needed for use with
    django.core.paginator.

    Usage:
        q1 = Thing.objects.filter(foo)
        q2 = Stuff.objects.filter(bar)
        qsc = QuerySetChain(q1, q2)
    """

    def __init__(self, *subquerysets):
        self.querysets = subquerysets

    def count(self):
        """
        Performs a .count() for all subquerysets and returns the number of
        records as an integer.
        """
        return sum(qs.count() for qs in self.querysets)

    def _clone(self):
        "Returns a clone of this queryset chain"
        return self.__class__(*self.querysets)

    def _all(self):
        "Iterates records in all subquerysets"
        return chain(*self.querysets)

    def __getitem__(self, index):
        """
        Retrieves an item or slice from the chained set of results from all
        subquerysets.
        """
        if type(index) is slice:
            return list(islice(self._all(), index.start, index.stop, 
                index.step or 1))
        else:
            return islice(self._all(), index, index+1).next()


class HighlightedSearch(object):
    def __init__(self):
        self.fragments = []
        self.highlighted = []

    def add_fragment(self, fragment, highlighted):
        if highlighted:
            self.fragments.append(fragment)
            self.highlighted.append(len(self.fragments) - 1)
        else:
            words = fragment.split()
            self.fragments.extend(words)

    def summary(self, size_limit):
        keeping = []
        size = 0
        last_index = 0
        for i in self.highlighted:
            if i < last_index:
                # we've wrapped past things included already, just keep moving
                continue

            backward = i - 5
            if backward < 0:
                backward = 0

            for j in range(backward, i):
                term = self.fragments[j]
                size += len(term) + 1
                keeping.append(term)

            term = self.fragments[i]
            keeping.append("<span class='fts_highlight'>%s</span>" % term)
            size += len(term)

            forward = i + 5
            if forward > len(self.fragments):
                forward = len(self.fragments)

            for j in range(i + 1, forward):
                term = self.fragments[j]
                size += len(term) + 1
                keeping.append(term)

            keeping.append('...')
            size += 3

            last_index = forward

            if size > size_limit:
                break

        return ' '.join(keeping)


class SummarizedPage(object):
    """Holder for Page objects with ability to return portions of its content
    for displaying summaries."""

    def __init__(self, page, block_key, summary_size, block=None,
            highlighted=False):
        self.page = page
        self.block = block
        self.block_key = block_key
        self.summary_size = summary_size
        self.highlighted = highlighted

    @classmethod
    def factory_from_highlighted_blocks(cls, blocks, summary_size):
        items = []
        for block in blocks:
            pages = block.page_set.all()
            for page in pages:
                sp = SummarizedPage(page, block.block_type.key, summary_size,
                    block=block, highlighted=True)
                items.append(sp)

        return items

    @property 
    def summary(self):
        value = ''
        if self.block and self.highlighted:
            value = self.summarize_highlighted(self.block.content_highlight, 
                self.summary_size)
        else:
            blocks = self.page.get_blocks(self.block_key)
            if len(blocks) != 0:
                value = self.summarize(blocks[0].content, self.summary_size)

        return value

    @classmethod
    def summarize(cls, text, size_limit):
        """Returns a substring no larger than size_limit, attempts to keep whole
        words by cutting the string at the last space."""
        # remove any html tags
        subtext = re.sub('<[^<]+?>', '', text)[:size_limit]
        if len(subtext) < size_limit:
            return subtext

        index = subtext.rfind(' ')
        if index == -1:
            return subtext

        subtext = subtext[:index]
        return subtext

    @classmethod
    def summarize_highlighted(cls, text, size_limit):
        # need to strip out all the html tags except for the <span> matching
        # tags
        # split everything up by tags
        pieces = []
        last_start = 0
        for match in re.finditer(r'<[^<]+?>', text):
            before = text[last_start:match.start()]
            if before:
                pieces.append(before)

            pieces.append(match.group(0))
            last_start = match.end()

        pieces.append(text[last_start:])

        # remove any tags that are not our span tag
        search = HighlightedSearch()
        span_stack = 0
        highlight_on = False
        for piece in pieces:
            if piece == "<span class='fts_highlight'>":
                highlight_on = True
            elif piece.startswith('<span'):
                span_stack += 1
            elif piece.startswith('</span>'):
                if span_stack == 0:
                    highlight_on = False
                else:
                    span_stack -= 1
            elif piece.startswith('<'):
                pass
            else:
                search.add_fragment(piece, highlight_on)

        return search.summary(size_limit)

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
        self.extension = None
        self._parse_node()

    @classmethod
    def factory_from_path(cls, path, ensure_file=False):
        """Takes a path and attempts to build a FileSpec object out of it.
        Raises AttributeError if path does not conform or isn't in either the
        public or private filespace."""
        if not os.path.exists(path):
            raise AttributeError('no such path')
        if ensure_file and not os.path.isfile(path):
            raise AttributeError('path was not a file')

        is_file = not os.path.isdir(path)
        if path.startswith(settings.MEDIA_ROOT):
            root_len = len(settings.MEDIA_ROOT)
            return FileSpec('public:%s' % path[root_len:], node_is_file=is_file)
        elif path.startswith(conf.site.private_upload):
            root_len = len(conf.site.private_upload)
            return FileSpec('private:%s' % path[root_len:], 
                node_is_file=is_file)

        raise AttributeError('path was not in public or private file space')

    @classmethod
    def factory_from_url(cls, url, ensure_file=False):
        if url.startswith(settings.MEDIA_URL):
            # url may be a public node
            root_len = len(settings.MEDIA_URL)
            node = 'public:%s' % url[root_len:]
        elif conf.site.private_upload_url \
                and url.startswith(conf.site.private_upload_url):
            # url may be a private node
            root_len = len(conf.site.private_upload_url)
            node = 'private:%s' % url[root_len:]

        spec = FileSpec(node, node_is_file=True)
        if ensure_file and not os.path.exists(spec.full_filename):
            raise AttributeError('no such path')

        return spec

    def _parse_node(self):
        pieces = self.node.split(':')
        try:
            self.file_type = pieces[0]
            x = urllib.unquote(pieces[1])
            if x and x[0] == '/':
                x = x[1:]

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
                raise Http404('bad node type')

            if self.node_is_file:
                self.set_filename(os.path.basename(x))
        except IndexError:
            raise Http404('bad node key')

    def set_filename(self, filename):
        self.basename = filename
        if '.' in filename:
            pieces = filename.split('.')
            self.extension = pieces[-1]
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
        name = 'users/%s' % user.username
        if self.relative_dir.startswith(name):
            return True

        return False

    def get_thumbnail(self, config=None):
        if not self.node_is_file:
            return None

        try:
            if not config:
                config = conf.site.auto_thumbnails['default']

            thumb_path = os.path.abspath(os.path.join(self.full_dir, 
                conf.site.auto_thumbnails['dir']))
            thumb_path = os.path.abspath(os.path.join(thumb_path, config))
            thumb_file = os.path.abspath(os.path.join(thumb_path,
                self.basename))

            if not os.path.exists(thumb_file):
                self.make_thumbnail(conf.site.auto_thumbnails['dir'],
                    config, conf.site.auto_thumbnails['config'][config][0],
                    conf.site.auto_thumbnails['config'][config][1])

            return FileSpec.factory_from_path(thumb_file, ensure_file=True)
        except KeyError:
            logger.exception('thumbnail requested but not properly configured')
            return None
        except AttributeError:
            logger.exception('thumbnail requested turned into bad path')
            return None

    def make_thumbnail(self, thumb_dir, thumb_key, width, height):
        image_dir = os.path.realpath(os.path.join(self.full_dir,
            thumb_dir, thumb_key))
        image_name = os.path.join(image_dir, self.basename)
        try:
            os.makedirs(image_dir)
        except:
            pass # already exists, do nothing

        # use PIL to create the thumbnail
        im = Image.open(self.full_filename)
        im.thumbnail((width, height), Image.ANTIALIAS)
        im.save(image_name, 'png')

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

    @property
    def url(self):
        if self.file_type == 'public':
            if self.node_is_file:
                return settings.MEDIA_URL + self.relative_filename
            else:
                return settings.MEDIA_URL + self.relative_dir
        elif self.file_type == 'private' and conf.site.private_upload:
            if self.node_is_file:
                return conf.site.private_upload_url + self.relative_filename
            else:
                return conf.site.private_upload_url + self.relative_dir

        return ''


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
        for x in sorted(os.listdir(spec.full_dir), cmp=locale.strcoll):
            if os.path.isdir(x):
                has_child_directories = True
                break

        if has_child_directories:
            file_hash['isLazy'] = True

        return file_hash

    # process any child directories
    children = []
    for x in sorted(os.listdir(spec.full_dir), cmp=locale.strcoll):
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
            'activate':True,
            'isLazy': True,
            'icon':'fatcow/folder.png',
        }
    else:
        public = files_subtree(spec, 2, expanded)
        if 'children' in public:
            public_node['children'] = public['children']
            public['children'][0]['activate'] = True

    tree = [public_node,]

    if conf.site.private_upload:
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

        tree.append(private_node)

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


def get_page_type(name):
    try:
        return PageType.objects.get(name=name)
    except PageType.DoesNotExist:
        return None


def get_block_type(key):
    try:
        return BlockType.objects.get(key=key)
    except BlockType.DoesNotExist:
        return None


def get_node(name):
    try:
        tx = NodeTranslation.objects.get(name=name)
        return tx.node
    except NodeTranslation.DoesNotExist:
        return None
