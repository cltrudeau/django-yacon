# yacon.models.pages.py
# blame ctrudeau chr(64) arsensa.com

import exceptions, logging
from django.db import models
from django.utils import simplejson as json
from django.core.exceptions import FieldError

from yacon.definitions import SLUG_LENGTH
from yacon.models.common import Language, TimeTrackedModel

logger = logging.getLogger(__name__)

# ============================================================================
# Page Management Classes
# ============================================================================

class PageType(TimeTrackedModel):
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


class BlockType(TimeTrackedModel):
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


class Page(TimeTrackedModel):
    language = models.ForeignKey(Language, related_name='+')
    slug = models.CharField(max_length=SLUG_LENGTH)
    title = models.CharField(max_length=25, blank=True, null=True)

    metapage = models.ForeignKey('yacon.MetaPage')

    # content for the page is stored in a series of blocks
    blocks = models.ManyToManyField(Block)

    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)
        self.after_slugs = None
        self.metapage_alias = None

    class Meta:
        app_label = 'yacon'

    def __unicode__(self):
        return 'Page(id=%s, path=%s)' % (self.id, self.uri)

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
        
        :returns: Page object corresponding to slugs[0] or None
        """
        try:
            page = Page.objects.get(slug=slugs[0], metapage__node=node)
            page.after_slugs = slugs[1:]
            return page
        except Page.DoesNotExist:
            pass

        # exact match was not found, check for aliases in the node
        metapages = MetaPage.objects.exclude(node=node, alias=None)
        for metapage in metapages:
            resolved = metapage.resolve_alias()
            try:
                page = Page.objects.get(slug=slugs[0], metapage=resolved)
                page.metapage_alias = metapage
                page.after_slugs = slugs[1:]
                return page
            except Page.DoesNotExist:
                pass

        # if you get here than no exact matches an no aliased matches
        return None

    def other_translations(self):
        """Returns a list of Page objects that represent other translations
        for this page.

        :returns: list of Page objects
        """
        pages = Page.objects.filter(metapage=self.metapage)
        return pages.exclude(id=self.id)

    def get_translation(self, language):
        """Returns the translated version of this Page in the given language,
        or None if there is no such translation.

        :param language: Language object specifying what translation to look
            for

        :returns: Page object in language or None
        """
        return self.metapage.get_translation(language)

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

    @property
    def uri(self):
        """Returns a valid URI that leads to this translated page.  Note that
        this may not be the URI that was used to find this content.  The URI
        is reconstructed using the language of this translation to get the
        slug path from the Node joined with the slug for this page.  

        Due to the fact that you can traverse the system through aliases, that
        you can parameterize a page with extra slugs and you can ask a page
        for its translation, there is no guarantee that the URI the user
        visited is the one returned by this method.

        If a MetaPage alias is registered with this object then the URI
        returned corresponds to that object rather than the absolute MetaPage.
        The MetaPage alias is set if the Page.find() method was used to find
        this page and the URI included aliases MetaPages.

        :returns: URI that can get you to this translated page
        """
        if self.metapage_alias != None:
            node_part = self.metapage_alias.node.node_to_path(self.language)
        else:
            node_part = self.metapage.node.node_to_path(self.language)

        if not node_part:
            return None

        return '//%s%s%s' % (self.metapage.node.site.domain, node_part, 
            self.slug)

    @property
    def lang_code(self):
        return self.language.identifier.upper()

    @property
    def all_blocks(self):
        """Shortcut property method for "blocks.all()" so it can be called
        inside of a template."""
        return self.blocks.all()


class DoubleAliasException(Exception):
    pass


class MetaPage(TimeTrackedModel):
    """This class represents a collection of translated pages in the CMS along
    with its placement in the doucment hierarchy.  All pages, even if they
    only have one translation, have a MetaPage.
    """
    node = models.ForeignKey('yacon.Node')
    _page_type = models.ForeignKey(PageType, blank=True, null=True)
    alias = models.ForeignKey('yacon.MetaPage', blank=True, null=True)

    class Meta:
        app_label = 'yacon'
        verbose_name = 'MetaPage'

    def __unicode__(self):
        result = 'MetaPage(id=%s, ' % self.id
        page = self.get_default_translation()
        if page == None:
            result += 'path=%s, EMPTY TRANSLATION' % (
                self.node.node_to_path())
        else: 
            result += 'path=%s' % page.uri

        if self.is_alias():
            result += ', ALIAS'

        result += ')'
        return result

    # -------------------------------------------
    # Getters -- need to use these so aliased values resolve properly

    @property
    def page_type(self):
        if self.is_alias():
            return self.resolve_alias()._page_type

        return self._page_type

    # -------------------------------------------
    # MetaPage Factories

    @classmethod
    def create_page(cls, node, page_type, title, slug, block_hash):
        """Creates, saves and returns a MetaPage object with a corresponding 
        Page object in the Site default language.

        :param node: node in Site hierarchy where the page lives
        :param page_type: PageType for this Page
        :param title: title for the page
        :param slug: slug for the page
        :param block_hash: hash of content mapping block_type to content

        :returns: MetaPage object
        """
        translation = Translation(language=node.site.default_language,
            title=title, slug=slug, block_hash=block_hash)
        return cls.create_translated_page(node, page_type, [translation])

    @classmethod
    def create_translated_page(cls, node, page_type, translations):
        """Creates, saves and returns a MetaPage object with multiple
        Page object translations.

        :param node: node in Site hierarchy where the page lives
        :param page_type: PageType for this Page
        :param translations: a list of Translation objects

        :returns: MetaPage object

        :raises: BadSlug, if any of the slugs are not valid
        """
        # create the Page
        metapage = MetaPage(node=node, _page_type=page_type)
        metapage.save()

        for tx in translations:
            node.validate_slug(tx.slug)
            page = Page(metapage=metapage, title=tx.title, slug=tx.slug, 
                language=tx.language)
            page.save()

            # add the content to the translation
            for key, value in tx.block_hash.items():
                block = Block(block_type=key, content=value)
                block.save()
                page.blocks.add(block)

        return metapage

    def create_alias(self, node):
        """An alias is a pointer to a MetaPage somewhere else in the Node
        hierarchy.  This creates an alias of the current MetaPage at the given
        point in the Node hierarchy.

        .. warning::
            Aliases should only be created using this method.  Aliasing an
            alias is not allowed to avoid complications and circular
            references.  If you create an alias by hand and get the reference
            wrong bad things could happen.

        :param node: node in Site hierarchy where the alias should be created

        :returns: MetaPage object that is an alias of self
        :raises: DoubleAliasException if you attempt to alias an alias
        """
        if self.is_alias():
            raise DoubleAliasException()

        metapage = MetaPage(node=node, alias=self)
        metapage.save()
        return metapage

    # -------------------------------------------
    # Alias Methods
    def is_alias(self):
        """Returns True if this MetaPage is an alias of another.

        :returns: True if self is an alias
        """
        return self.alias != None

    def resolve_alias(self):
        """Returns the MetaPage that self's alias points to.  

        .. warning::
            Aliases should only be created with :func:`MetaPage.create_alias`.  
            This method does not check for circular references or aliases of
            aliases.  If the alias was not created properly this method could
            loop forever.

        :returns: MetaPage that this page is aliased to, or None
        """
        if not self.is_alias():
            return None

        return self.alias

    # -------------------------------------------
    # Search Methods

    def get_translation(self, language):
        """Returns a Page object for this MetaPage in the given language.

        :param language: Language for the corresponding translation

        :returns: Page object or None
        """
        mp = self
        if self.is_alias():
            mp = self.resolve_alias()

        try:
            page = Page.objects.get(metapage=mp, language=language)
            if mp != self:
                page.metapage_alias = self
        except Page.DoesNotExist:
            return None

        return page

    def get_translations(self, ignore_default=False):
        """Returns a list of Page objects representing the translated content
        for this MetaPage.

        :param ignore_default: if True the default language will not be
            returned in the list; defaults to False

        :returns: list of Pages
        """
        mp = self
        if self.is_alias():
            mp = self.resolve_alias()

        pages = Page.objects.filter(metapage=mp)
        if ignore_default:
            # remove the default language from the list
            pages = pages.exclude(language=mp.node.site.default_language)

        if mp != self:
            for page in pages:
                page.metapage_alias = self

        return pages

    def get_default_translation(self):
        """Returns the Page object for the site default language

        :returns: Page object or None
        """
        mp = self
        if self.is_alias():
            mp = self.resolve_alias()

        try:
            page = Page.objects.get(metapage=mp, 
                language=mp.node.site.default_language)
            if mp != self:
                page.metapage_alias = self
        except Page.DoesNotExist:
            return None

        return page
