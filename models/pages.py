# yacon.models.pages.py
# blame ctrudeau chr(64) arsensa.com

import exceptions, logging
from django.db import models
from django.utils import simplejson as json
from django.core.exceptions import FieldError

from yacon.models.hierarchy import Site, Node

logger = logging.getLogger(__name__)

# ============================================================================
# Page Management Classes
# ============================================================================

class PageType(models.Model):
    """Defines how a page is constructed, tied to a template for rendering."""

    name = models.CharField(max_length=25, unique=True)
    template = models.CharField(max_length=50)

    class Meta:
        app_label = 'yacon'


class BadContentHandler(exceptions.Exception):
    pass


class BlockType(models.Model):
    """Contains the name of a ContentHandler object which is used for managing
    content on a page.  A PageType references to multiple BlockType objects"""
    name = models.CharField(max_length=25, unique=True)
    key = models.CharField(max_length=25, unique=True)

    # '%s.%s' % (mod, content_handler) should produce the fully qualified name
    # of an object that inherits from ContentHandler (or at least duck-types)
    module_name = models.CharField(max_length=100)
    content_handler_name = models.CharField(max_length=50)
    content_handler_parms = models.TextField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        try:
            parms = kwargs['content_handler_parms']
        except KeyError:
            # no content_handler_parms passed in, store empty dict
            parms = {}

        serialized = json.JSONEncoder().encode(parms)
        kwargs['content_handler_parms'] = serialized

        super(BlockType, self).__init__(*args, **kwargs)
        self.content_handler_instance = None

    def __unicode__(self):
        return u'BlockType(name=%s, key=%s)' % (self.name, self.key)

    class Meta:
        app_label = 'yacon'

    def get_content_handler_parms(self):
        """De-serializes and returns a hash representing the parameters for
        the content handler"""
        parms = json.loads(self.content_handler_parms)
        return parms

    def set_content_handler_parms(self, parms):
        serialized = json.JSONEncoder.encode(parms)
        self.content_handler_parms = serialized
        self.save()

    def get_content_handler(self):
        if self.content_handler_instance != None:
            logger.debug('returning cached content_handler_instance')
            return self.content_handler_instance

        # instantiate a content handler
        try:
            logger.debug('about to import mod %s.%s' % (self.module_name,
                self.content_handler_name))

            mod = __import__(self.module_name, globals(), locals(),
                [self.content_handler_name])
            logger.debug('mod import successful')
        except Exception, e:
            logger.exception('importing mod caused exception')
            t = e.__class__.__name__
            msg = \
"""
An exception was caught during the import of the user specified
module "%s".  The exception was: "%s" 
with the message:

%s

Exceptions during import are usually caused by syntax errors or 
import errors in the module.
""" % (self.module_name, t, e)

            bch = BadContentHandler(msg) 
            raise bch

        try:
            logger.debug('getting class object for content handler')
            klass = getattr(mod, self.content_handler_name)
            logger.debug('found class for content handler')
        except Exception, e:
            logger.exception(\
                'getting class object for content handler caused exception')
            t = e.__class__.__name__
            msg = \
"""
An exception was caught during the retrieval of the user specified
class "%s" from the module "%s".  The 
exception was: "%s" with the message:

%s
""" % (self.content_handler_name, self.module_name, t, e)

            bch = BadContentHandler(msg)
            raise bch

        try:
            parms = self.get_content_handler_parms()
            logger.debug('instantiatiing class with parms: %s' % parms)

            self.content_handler_instance = klass(self, parms)
        except Exception, e:
            logger.exception('instantiating content handler caused exception')
            t = e.__class__.__name__
            msg = \
"""
An exception was caught during the instantiation of the user specified
class "%s" from the module "%s".  The 
exception was: "%s" with the message:

%s

Instantiation errors are usually caused by problems in the constructor.
""" % (self.module_name, self.content_handler_name, t, e)

            bch = BadContentHandler(msg)
            raise bch

        logger.debug('returning handler: %s' % self.content_handler_instance)
        return self.content_handler_instance


class Block(models.Model):
    block_type = models.ForeignKey(BlockType)

    parameters = models.TextField(null=True, blank=True)
    content = models.TextField()

    # management of owner, groups, privileges etc. should go here (?)

    def __init__(self, *args, **kwargs):
        super(Block, self).__init__(*args, **kwargs)
        self.is_editable = False

    def __unicode__(self):
        return u'Block(block_type=%s, content=%s)' % (self.block_type,
            self.content)

    class Meta:
        app_label = 'yacon'

    def render(self, request):
        """Returns a rendered version of the block via its ContentHandler"""

        handler = self.block_type.get_content_handler()
        return handler.render(request, self)


class Page(models.Model):
    node = models.ForeignKey(Node)
    slug = models.CharField(max_length=25, unique=True)
    _alias = models.ForeignKey('self', blank=True, null=True)
    _title = models.CharField(max_length=25, blank=True, null=True)
    _page_type = models.ForeignKey(PageType, blank=True, null=True)

    # what pages this content apperas on
    _blocks = models.ManyToManyField(Block)

    class Meta:
        app_label = 'yacon'

    # -------------------------------------------
    # Constructors/Factories

    def __init__(self, *args, **kwargs):
        """A Page object represents a page to be rendered for a given slug
        within a location in a hierarchy.  In order to allow the page to exist
        in multiple places, the Page object can contain an alias to another
        Page object.  An alias, although still a Page object, can only be
        constructed through the create_alias() call on an existing Page.

        The following parameters are always expected to construct a page:

        @param node -- hierarchical node of this page
        @param slug -- slug within the hierarchy uniquely identifying this
            page
        @param title -- the title of this page
        @param page_type -- a PageType object that defines the template that
            this Page instance will be using

        The 'title' and 'page_type' parameters correspond to private fields,
        the private fields should not be used to construct the object
        directly.
        """
        if 'title' in kwargs and 'page_type' not in kwargs:
                raise FieldError('Parameter "title" is mandatory')

        if 'page_type' in kwargs and 'title' not in kwargs:
                raise FieldError('Parameter "page_type" is mandatory')

        if 'title' in kwargs:
            kwargs['_title'] = kwargs['title']
            del kwargs['title']

        if 'page_type' in kwargs:
            kwargs['_page_type'] = kwargs['page_type']
            del kwargs['page_type']

        # parms have been checked and set correctly, just call parent
        super(Page, self).__init__(*args, **kwargs)

    def create_alias(self, node, slug):
        """Returns a Page object that is an alias to this Page instance.
        Attempting to create an alias of an alias will result in an
        AttributeError is raised.  The save() call is done on the newly
        created object so a successful call results in a new entry in the
        database.

        @param node -- node in hierarchy for the newly aliased Page
        @param slug -- slug uniquely identifying the alias within the node
            hierarchy

        @returns Page -- a new Page object that is an alias to this one
        """
        if self._alias != None:
            raise AttributeError('Aliases of aliases not allowed')

        page = Page(node=node, slug=slug, _alias=self)
        page.save()
        return page

    # -------------------------------------------
    # Accessors for referencing private fields

    @property
    def title(self):
        if self._alias == None:
            return self._title

        return self._alias.title

    @property 
    def page_type(self):
        if self._alias == None:
            return self._page_type

        return self._alias.page_type

    @property 
    def blocks(self):
        if self._alias == None:
            return self._blocks

        return self._alias.blocks

    # -------------------------------------------
    # Accessors
    def is_alias(self):
        return self._alias != None

    def get_uri(self, language=None):
        return '%s%s' % (self.node.node_to_path(language), self.slug)

    # -------------------------------------------
    # Block Finding Methods

    def get_blocks_by_key(self, key):
        """Returns a list of blocks with the corresponding key"""
        return list(self.blocks.filter(block_type__key=key))


# ============================================================================
# Helper Methods
# ============================================================================

def page_list(site, uri):
    """Returns a list of pages that are found underneath the node
    corresponding to the given URI.
    
    @param uri -- URI corresponding to a Node object to find pages.  If the
        URI is fully qualified (i.e. specifies a slug) only a single page is 
        returned.  If the node doesn't include a slug then all pages are
        returned.
    @return -- list of pages for the Node; empty list for invalid URI or one
        with no pages associated"""

    parsed = site.parse_path('/' + uri)
    if parsed.node == None:
        # weren't able to parse the path
        return []
        
    if len(parsed.slugs_after_node) > 0:
        # find the pages that corresponds to the uri
        try:
            page = Page.objects.get(node=parsed.node, 
                slug=parsed.slugs_after_node[0])
            return [page]
        except Page.DoesNotExist:
            return []

    # only get here if there was no slugs in the URI -> search for all pages
    try:
        return Page.objects.filter(node=parsed.node)
    except Page.DoesNotExist:
        return []
