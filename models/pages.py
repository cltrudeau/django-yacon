# yacon.models.pages.py
# blame ctrudeau chr(64) arsensa.com

import exceptions
from django.db import models
from yacon.models.hierarchy import Node, ContentHierarchy

# ============================================================================
# Page Management Classes
# ============================================================================

class PageType(models.Model):
    """Defines how a page is constructed, tied to a template for rendering.
    Includes name of a ContentHandler class that is used to"""

    name = models.CharField(max_length=25, unique=True)
    template = models.CharField(max_length=50)

    # One-to-Many FK on BlockSpecifier

    class Meta:
        app_label = 'yacon'


class BlockSpecifier(models.Model):
    """Contains the name of a ContentHandler object which is used for managing
    content on a page.  A PageType references to multiple BlockSpecifiers"""
    name = models.CharField(max_length=25, unique=True)
    key = models.CharField(max_length=25, unique=True)
    pagetype = models.ForeignKey(PageType)

    # '%s.%s' % (mod, content_handler) should produce the fully qualified name
    # of an object that inherits from ContentHandler (or at least duck-types)
    mod = models.CharField(max_length=100)
    content_handler = models.CharField(max_length=50)

    class Meta:
        app_label = 'yacon'

class BadContentHandler(exceptions.Exception):
    pass

class Block(models.Model):
    specifier = models.ForeignKey(BlockSpecifier)

    parameters = models.TextField()
    content = models.TextField()

    # management of owner, groups, privileges etc. should go here (?)

    class Meta:
        app_label = 'yacon'

    @property
    def render(self):
        """Uses associated ContentHandler to render and return our _content 
        blob"""

        # instantiate our ContentHandler
        try:
            mod = __import__(self.specifier.mod, globals(), locals(),
                [self.specifier.content_handler])
        except Exception, e:
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

            bch = BadContentHandler(msg % (self.specifier.mod, t, e))
            raise bch

        try:
            klass = getattr(mod, self.specifier.content_handler)
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
            handler = klass(self)
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

        return handler.render()


class Page(models.Model):
    title = models.CharField(max_length=25)
    slug = models.CharField(max_length=25, unique=True)
    node = models.ForeignKey(Node)
    pagetype = models.ForeignKey(PageType)

    # what pages this content apperas on
    blocks = models.ManyToManyField(Block)

    class Meta:
        app_label = 'yacon'

    def content_dict(self):
        """Returns a dictionary of content blocks.  Keys to the dictionary are
        based on the Block's key.  If there is more than one Block with the
        same key then the corresponding value will be a list."""

        data = {}
        for block in self.blocks.all():
            key = block.specifier.key
            if key in data:
                # key already exists in data, check if it is a list
                value = data[key]
                if type(value) is list:
                    # already has a list, add to it
                    data[key].append(value)
                else:
                    # had single value, change it to a list
                    data[key] = [value, block]
            else:
                # key wasn't in data, add this key/value pair
                data[key] = block

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
