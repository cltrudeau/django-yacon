# yacon.models.pages.py
# blame ctrudeau chr(64) arsensa.com

import exceptions, logging
from django.db import models
from django.utils import simplejson as json
from django.core.exceptions import FieldError

from yacon.definitions import SLUG_LENGTH
from yacon.models.language import Language

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
    """Exception raised when an attempt is made to load or manipulate a
    ContentHandler and something goes wrong.  See:
    BlockType.get_content_handler()
    """
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
    """Defines a block of content for the CMS"""
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

# ============================================================================
# Page & Supporting Classes
# ============================================================================

class Translation(object):
    """Temporary class used to help construct Page and PageTranslation
    objects.  Used in conjunction with Page factory methods for creating a
    page and its translated contents.
    """
    def __init__(self, language, title, slug, block_hash):
        """Constructor

        :param language: Language object representing what language the blocks
            contained with are writen in
        :param title: title of the translated page content
        :param slug: slug of the translated page content
        :param block_hash: a hash mapping BlockType objects to content
        """
        self.language = language
        self.title = title
        self.slug = slug
        self.block_hash = block_hash


class PageTranslation(models.Model):
    language = models.ForeignKey(Language, related_name='+')
    slug = models.CharField(max_length=SLUG_LENGTH)
    title = models.CharField(max_length=25, blank=True, null=True)

    page = models.ForeignKey('yacon.Page')

    # content for the page is stored in a series of blocks
    blocks = models.ManyToManyField(Block)

    def __init__(self, *args, **kwargs):
        super(PageTranslation, self).__init__(*args, **kwargs)
        self.after_slugs = None

    class Meta:
        app_label = 'yacon'

    # ---------------------------
    # Search
    @classmethod
    def find(cls, node, slugs):
        """Seraches for a translated page within the given Node with the
        corresponding slug.

        :param node: Node to search for the translated page 
        :param slugs: list of slugs, first of which is the key for the page,
            remainder are stored in the returned object in case they're needed
            as parameters
        
        :returns: PageTranslation object corresponding to slugs[0] or None
        """
        try:
            pt = PageTranslation.objects.get(slug=slugs[0], page__node=node)
        except PageTranslation.DoesNotExist:
            return None

        return pt

    def other_translations(self):
        """Returns a list of PageTranslation objects that represent other
        translations for this page.

        :returns: list of PageTranslation objects
        """
        pts = PageTranslation.objects.filter(page=self.page)
        return pts.exclude(id=self.id)

    # -------------------------------------------
    # Block Handling Methods

    def get_blocks(self, key):
        """Returns a list of blocks from this translated page

        :param key: key for blocks to be retrieved

        :returns: list of Block objects
        """
        return self.blocks.filter(block_type__key=key)

    def get_block_keys(self):
        """Returns a list of the keys for which there is Block content for
        this page

        :returns: list of keys
        """
        bts = self.blocks.value_list('block_type', flat=True).distinct()
        return [bt.key for bt in bts]


    def create_block(self, block_type, content):
        """Creates and saves a new Block and adds it to this translated page

        :param block_type: BlockType for the Block being created
        :param content: content of Block

        :returns: the created, saved and added Block
        """
        block = Block(block_type=block_type, content=content)
        block.save()
        self.blocks.add(block)
        return block

    # ---------------------------
    # Utility Methods

    def get_uri(self):
        """Returns a valid URI that leads to this translated page.  Note that
        this may not be the URI that was used to find this content.  The URI
        is reconstructed using the language of this translation to get the
        slug path from the Node joined with the slug for this page.  

        Due to the fact that you can traverse the system through aliases, that
        you can parameterize a page with extra slugs and you can ask a page
        for its translation, there is no guarantee that the URI the user
        visited is the one returned by this method.

        :returns: URI that can get you to this translated page
        """
        node_part = self.page.node.node_to_path(self.language)
        return '%s%s' % (node_part, self.slug)


class Page(models.Model):
    """This class represents a multi-lingual page in the CMS.  The actual
    content is stored in the PageTranslation objects that this Page points to.
    Even in a single-language system, content is stored in a "translation".
    """
    node = models.ForeignKey('yacon.Node')
    page_type = models.ForeignKey(PageType, blank=True, null=True)

    class Meta:
        app_label = 'yacon'

    # -------------------------------------------
    # Page Factories

    @classmethod
    def create_page(cls, node, page_type, title, slug, block_hash):
        """Creates, saves and returns a Page object in the Site default
        language.

        :param node: node in Site hierarchy where the page lives
        :param page_type: PageType for this Page
        :param title: title for the page
        :param slug: slug for the page
        :param block_hash: hash of content mapping block_type to content

        :returns: Page object
        """
        translation = Translation(language=node.site.default_language,
            title=title, slug=slug, block_hash=block_hash)
        return cls.create_translated_page(node, page_type, [translation])

    @classmethod
    def create_translated_page(cls, node, page_type, translations):
        """Creates, saves and returns a Page object with multiple
        translations.

        :param node: node in Site hierarchy where the page lives
        :param page_type: PageType for this Page
        :param translations: a list of Translation objects

        :returns: Page object
        """
        # create the Page
        page = Page(node=node, page_type=page_type)
        page.save()

        for tx in translations:
            pt = PageTranslation(page=page, title=tx.title, slug=tx.slug, 
                language=tx.language)
            pt.save()

            # add the content to the translation
            for key, value in tx.block_hash.items():
                block = Block(block_type=key, content=value)
                block.save()
                pt.blocks.add(block)

        return page

    # -------------------------------------------
    # Search Methods

    def get_translation(self, language):
        """Returns a PageTranslation object for this Page in the given
        language.

        :param language: Language for the corresponding translation

        :returns: PageTranslation object or None
        """
        try:
            return PageTranslation.objects.get(page=self, language=language)
        except PageTranslation.DoesNotExist:
            return None

    def get_translations(self, ignore_default=False):
        """Returns a list of PageTranslation objects representing the
        translated content for this page.

        :param ignore_default: if True the default language will not be
            returned in the list; variable defaults to False

        :returns: list of PageTranlsations
        """
        if not ignore_default:
            return PageTranslation.objects.filter(page=self)

        # ignore default language
        return PageTranslation.objects.exclude(page=self, 
            language=self.node.site.default_language)

    def get_default_translation(self):
        """Returns the PageTranslation object for the site default language

        :returns: PageTranslation object or None
        """
        try:
            pt = PageTranslation.objects.get(page=self, 
                language=self.node.site.default_language)
        except PageTranslation.DoesNotExist:
            return None

        return pt
