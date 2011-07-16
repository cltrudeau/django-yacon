# yacon.models.pages.py
# blame ctrudeau chr(64) arsensa.com

import exceptions, logging
from django.db import models
from django.utils import simplejson as json
from yacon.models.hierarchy import Node, ContentHierarchy

# ============================================================================
# Page Management Classes
# ============================================================================

class PageType(models.Model):
    """Defines how a page is constructed, tied to a template for rendering."""

    name = models.CharField(max_length=25, unique=True)
    template = models.CharField(max_length=50)

    class Meta:
        app_label = 'yacon'


class BlockSpecifier(models.Model):
    """Contains the name of a ContentHandler object which is used for managing
    content on a page.  A PageType references to multiple BlockSpecifiers"""
    name = models.CharField(max_length=25, unique=True)
    key = models.CharField(max_length=25, unique=True)

    # '%s.%s' % (mod, content_handler) should produce the fully qualified name
    # of an object that inherits from ContentHandler (or at least duck-types)
    mod = models.CharField(max_length=100)
    content_handler = models.CharField(max_length=50)
    content_handler_parms = models.TextField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        try:
            parms = kwargs['content_handler_parms']
        except KeyError:
            # no content_handler_parms passed in, store empty dict
            parms = {}

        serialized = json.JSONEncoder().encode(parms)
        kwargs['content_handler_parms'] = serialized

        super(BlockSpecifier, self).__init__(*args, **kwargs)
        self.content_handler_instance = None

    def __unicode__(self):
        return u'BlockSpecifier(name=%s, key=%s)' % (self.name, self.key)

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
        print 'inside get-content_handler()'
        if self.content_handler_instance != None:
            logging.debug('returning cached content_handler_instance')
            return self.content_handler_instance

        # instantiate a content handler
        try:
            print 'loading mod'
            mod = __import__(self.specifier.mod, globals(), locals(),
                [self.specifier.content_handler])
            print 'loaded mod'
            logging.debug('imported mod')
        except Exception, e:
            print 'exception'
            t = e.__class__.__name__
            msg = \
"""
An exception was caught during the import of the user specified
module "%s".  The exception was: "%s" 
with the message:

%s

Exceptions during import are usually caused by syntax errors or 
import errors in the module.
"""

            print 'creating bch'
            try:
                bch = BadContentHandler(msg % (self.specifier.mod, t, e))
            except Exception, e:
                print e
            print 'created bch: ', bch
            logging.error('%s' % bch)
            raise bch

        try:
            klass = getattr(mod, self.specifier.content_handler)
            logging.debug('found class')
        except Exception, e:
            t = e.__class__.__name__
            msg = \
"""
An exception was caught during the retrieval of the user specified
class "%s" from the module "%s".  The 
exception was: "%s" with the message:

%s
"""
            bch = BadContentHandler(msg % (self.specifier.content_handler, 
                self.specifier.mod, t, e))
            raise bch

        try:
            self.content_handler_instance = klass(self,
                self.get_content_handler_parms())
            logging.debug('instantiated class')
        except Exception, e:
            t = e.__class__.__name__
            msg = \
"""
An exception was caught during the instantiation of the user specified
class "%s" from the module "%s".  The 
exception was: "%s" with the message:

%s

Instantiation errors are usually caused by problems in the constructor.
"""
            bch = BadContentHandler(msg % (self.specifier.mod, 
                self.specifier.content_handler, t, e))
            raise bch

        logging.debug('returning handler: %s' % self.content_handler_instance)
        return self.content_handler_instance

class BadContentHandler(exceptions.Exception):
    pass

class Block(models.Model):
    specifier = models.ForeignKey(BlockSpecifier)

    parameters = models.TextField(null=True, blank=True)
    content = models.TextField()

    # management of owner, groups, privileges etc. should go here (?)

    def __init__(self, *args, **kwargs):
        super(Block, self).__init__(*args, **kwargs)
        self.context = {}
        self.is_editable = False

    def extend_context(self, context):
        self.context.update(context)

    def __unicode__(self):
        return u'Block(specifier=%s, content=%s)' % (self.specifier,
            self.content)

    class Meta:
        app_label = 'yacon'

    @property
    def render(self):
        """Uses associated ContentHandler to render and return our _content 
        blob"""
        logging.debug('starting to render')

        handler = self.specifier.get_content_handler()
        logging.debug('calling render() on handler %s' % handler)
        return handler.render(self.context['request'], self.context['uri'],
            self.context['node'], self.context['slugs'])


class Page(models.Model):
    title = models.CharField(max_length=25)
    slug = models.CharField(max_length=25, unique=True)
    node = models.ForeignKey(Node)
    pagetype = models.ForeignKey(PageType)

    # what pages this content apperas on
    blocks = models.ManyToManyField(Block)

    class Meta:
        app_label = 'yacon'

    def get_blocks_by_key(self, key):
        """Returns a list of blocks with the corresponding key"""
        results = []
        for block in self.blocks.all():
            if block.specifier.key == key:
                results.append(block)

        return results

    def content_dict(self, request, uri, slugs):
        """Builds a content dictionary comprised of all of the blocks for this
        page.  Each block has context attached to it for later rendering (i.e.
        the request, uri and slugs passed into this method) and then is
        grouped by the block's key in a list.  The content dictionary is a
        dictionary of block keys corresponding to lists of blocks for that
        key.
        
        @param request -- the HTTP request object
        @param uri -- URI used in the request
        @param slugs -- list of slugs associated with the content, slug[0]
            will correspond to the content, values after that are optional"""

        data = {}
        for block in self.blocks.all():
            block.extend_context({'request':request, 'uri':uri, 'slugs':slugs,
                'node':self.node})
            key = block.specifier.key
            if key not in data:
                # no key in the data dictionary yet, add an empty list
                data[key] = []

            # add the block to the data dictionary list
            data[key].append(block)

        logging.debug('returning content dictionary: %s' % data)
        return data

# ============================================================================
# Helper Methods
# ============================================================================

def page_list(uri):
    """Returns a list of pages that are found underneath the node
    corresponding to the given URI.
    
    @param uri -- URI corresponding to a Node object to find pages.  If the
        URI is fully qualified (i.e. specifies a slug) only a single page is 
        returned.  If the node doesn't include a slug then all pages are
        returned.
    @return -- list of pages for the Node; empty list for invalid URI or one
        with no pages associated"""

    parsed = ContentHierarchy.parse_path('/' + uri)
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
