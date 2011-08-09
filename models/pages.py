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


class PageData(models.Model):
    """PageData represents the contents of a page in the CMS.  This class
    should not be used directly as it encapsulates multiple translations of
    the content; instead the Page class should be used to create and access
    pages in the CMS.
    """
    node = models.ForeignKey('yacon.Node')
    alias = models.ForeignKey('self', blank=True, null=True)
    page_type = models.ForeignKey(PageType, blank=True, null=True)

    # a page is comprised of blocks which can have multiple translated
    # versions
    blocks = models.ManyToManyField(Block, through='yacon.BlockTranslation')

    class Meta:
        app_label = 'yacon'


# ============================================================================
# Page Class
# ============================================================================

class Page(object):
    """A Page object represents a page of the CMS that is to be rendered.
    This is a convience object that wraps a PageData object, exposing just the
    appropriate content based on the Language the Page is constructed with.
    """

    # -------------------------------------------
    # Page Factories
    @classmethod
    def _factory(cls, page_data, language):
        """Constructs a Page object by wrapping a PageData django model object

        @param page_data: a PageData object to wrap
        @param language: the Language to associate with the rendering page

        @returns Page: a Page object based on a PageData and Language object
        """
        try:
            pt = PageTranslation.objects.get(page_data=page_data,
                language=language)
        except PageTranslation.DoesNotExist:
            # no PageTranslation for given PageData/Language
            return None

        page = Page()
        page._page_data = page_data
        page.language = language
        page.translation = pt
        return page

    @classmethod
    def create_page_with_default_language(cls, node, page_type, slug, 
        title, translations={}):
        """Factory method for Page objects which constructs and saves the
        underlying PageData django model object, wraps it in a Page object and
        returns that Page object.  
        
        Slug and title fields are assumed to be in the Site's default
        Language.
        
        @param node: Node object of where this page should be created in the
            hierarchy.  This is also used to determine what Site the PageData
            is in.
        @param page_type: PageType object identifying the template to be
            associated with this PageData
        @param slug: slug uniquely identifying this page within the Node
            object container.  Multiple slugs in different languages can be
            used to identify the multiple language versions of this page; this
            slug is given in the Site's default language
        @param title: title of the page.  Multiple titles in different
            languages can be associated with the page; this title is given in
            the Site's default language
        @param translations: a dictionary of Language objects mapping to
            (slug, title) tuples for the translations of the slug and title
            pairs

        @returns Page: creates and saves a PageData and returns a Page wrapper
        """
        lang = node.site.default_language
        translations[lang] = (slug, title)
        return cls.create_page(node, page_type, lang, translations)

    @classmethod
    def create_page(cls, node, page_type, language, translations):
        """Factory method for Page objects which constructs and saves the
        underlying PageData django model object, wraps it in a Page object and
        returns that Page object.

        @param node: Node object of where this page should be created in the
            hierarchy.  This is also used to determine what Site the PageData 
            is in.
        @param page_type: PageType object identifying the template to be
            associated with this PageData
        @param language: Language object for the language to use when building
            the Page wrapper
        @param translations: a dictionary of Language objects mapping to
            (slug, title) tuples for the translations of the slug and title
            pairs.

        @returns Page: creates and saves a PageData object and returns the 
            Page wrapper
        @raises: AttributeError if at least one translation mapping doesn't
            exist
        """
        if len(translations) == 0:
            raise AttributeError('At least one translation must be provided')

        page_data = PageData(node=node, page_type=page_type)
        page_data.save()

        PageTranslation.create_translations(page_data, translations)
        return cls._factory(page_data, language)

    @classmethod
    def find_page(cls, node, slug):
        """Searches for a PageData object within the given Node using the
        given slug.  Uses the slug to determine the Language for a Page object
        and constructs it.

        @param node: Node to search for PageData within
        @param slug: slug identifier for PageData

        @returns Page: the found Page object or None if there is no such slug
            in the given Node
        """
        try:
            pt = PageTranslation.objects.get(slug=slug, page_data__node=node)
        except PageTranslation.DoesNotExist:
            return None

        return cls._factory(pt.page_data, pt.language)

    def create_alias_with_default_language(self, node, slug, title=None, 
        translations={}):
        """Creates a PageData object that is an alias to this Page's PageData
        object, wraps the new object in a Page and returns it.

        Slug field is assumed to be in the Site's default Language.
        
        Attempting to create an alias of an alias will result in an
        AttributeError being raised.  

        @param node: node in hierarchy for the newly aliased PageData
        @param slug: slug uniquely identifying the alias within the node
            hierarchy given in the Site's default language
        @param title: title for the aliased page.  If None will use the 
            original Page's title
        @param translations: a dictionary mapping Language objects to slugs
            for each translation of a slug for this alias

        @returns Page: a new Page object wrapping the newly created alias
            PageData object 
        @raises AttributeError: if method is called on a PageData that is 
            already an alias
        """
        lang = node.site.default_language

        if title == None:
            title = self.title

        translations[lang] = (slug, title)
        return self.create_alias(node, lang, translations)

    def create_alias(self, node, language, translations):
        """Creates a PageData object that is an alias to this Page's PageData
        object, wraps the new object in a Page and returns it.
        
        Attempting to create an alias of an alias will result in an
        AttributeError being raised.  The save() call is done on the newly
        created object before it is returned.

        @param node: node in hierarchy for the newly aliased Page
        @param language: Language object to use for the rendering Page object
            created that wraps the newly aliased PageData
        @param translations: a dictionary mapping Language objects to slugs
            for each translation of a slug for this alias.  

        @returns Page: a new Page object wrapping the newly created alias
            PageData object
        @raises AttributeError: if method is called on a Page that is already
            an alias or if the translations dictionary is empty
        """
        if len(translations) == 0:
            raise AttributeError('At least one translation must be provided')

        if self.page_data.alias != None:
            raise AttributeError('Aliases of aliases not allowed')

        page_data = PageData(node=node, alias=self.page_data)
        page_data.save()

        PageTranslation.create_translations(page_data, translations)
        return self._factory(page_data, language)

    def get_page_translation(self, language):
        """Returns a translated version of this Page in the given Language.
        If no translation exists for that Language then returns None.

        @param language: Language object to get a translated version of this
            Page
        @returns Page: a new Page object for the given Language or None if
            there is no such translation
        """
        return Page._factory(self.page_data, language)

    # -------------------------------------------
    # Getters 
    @property
    def title(self):
        """Returns the title of this Page.

        @returns string: title of this Page
        """
        return self.translation.title

    @property
    def page_data(self):
        """Returns the PageData object of this Page or if the PageData is an
        alias then it returns the alias's originating PageData object.

        @returns PageData: PageData for this Page or its alias
        """
        pd = self._page_data
        if pd.alias != None:
            pd = self._page_data.alias

        return pd

    @property 
    def page_type(self):
        """Returns the PageType object associated with this Page.

        @returns PageType: PageType object associated with this Page
        """
        return self.page_data.page_type

    def blocks(self, *args, **kwargs):
        """Returns a list of Block objects that are associated with this page

        @param **kwargs: optional set of key word arguments can be used to
            filter the Blocks that come back, filters are the same as used in
            regular model queries

        @returns list: list of Block objects for this Page in its Language
        """
        blocks = Block.objects.filter(pagedata=self.page_data,
            blocktranslation__language=self.language)

        if len(kwargs) > 0:
            blocks = blocks.filter(**kwargs)

        return list(blocks)

    def is_alias(self):
        """Returns True if this Page is an alias to another"""
        return self.page_data.alias != None

    def get_uri(self):
        """Returns the URI for this Page.

        @returns string: URI for this Page in its currently rendered language
        """
        node_part = self.page_data.node.node_to_path(language)
        return '%s%s' % (node_part, self.translation.slug)

    def other_translations(self):
        """Returns a list of Language objects representing the languages for
        which there is content associated with the underlying PageData not
        including the language being rendered by this Page object.

        @returns list: a list of Language objects for which there are other
            translations of ths Page
        """
        bts = BlockTranslations.objects.filter(page_data=self.page_data,
            language__ne=self.language)
        return bts.values('language').distinct()

    # -------------------------------------------
    # Block Finding Methods

    def get_blocks_by_key(self, key):
        """Returns a list of Blocks that have a BlockType with the key passed
        in.  
        
        @param key: the key for which Block objects that have a BlockType with
            this key should be returned
        @returns list: list of Block objects
        """
        bts = BlockTranslation.objects.filter(block__block_type__key=key,
            page_data=self.page_data, language=self.language)
        return bts.values_list('block', flat=True)

    # -------------------------------------------
    # Block Handling Methods
    def create_block(self, block_type, content, language=None):
        """Creates and saves a new Block and adds it to this Page's PageData

        @param block_type: BlockType for the Block being created
        @param content: content of Block
        @param language: Language the content is written in.  If None then
            Site default language is used

        @returns Block: the created, saved and added Block
        """
        block = Block(block_type=block_type, content=content)
        block.save()
        self.add_block(block, language)
        return block

    def add_block(self, block, language=None):
        """Adds a Block object to this Page's PageData object.  If no Language 
        parameter is passed in then the Site's default Language is used

        @param block: block to be added to this page
        @param language: Language object indicating the language of this
            Block.  If None given then the Site's default language is used
        """
        if language == None:
            language = self.node.site.default_language

        bt = BlockTranslation(page_data=self.page_data, block=block, 
            language=language)
        bt.save()

    def remove_block(self, block):
        """Removes a block from this Page's PageData.  Note that this does
        not delete the Block itself, merely removes the association with the
        PageData.  As a single Block can be associated with multiple pages,
        the Block has to be deleted explicitly.

        If the block given does not correspond to this Page object then
        AttributeError is raised.

        @param block: Block object to be removed from this Page's PageData
            object

        @raises AttributeError: if the Block is not already associated with
            this Page's PageData object
        """
        try:
            bt = BlockTranslation.objects.get(page_data=self.page_data, 
                block=block)
            bt.remove()
        except BlockTranslation.DoesNotExist:
            raise AttributeError('Block not associated with this Page')


# ============================================================================
# Translation Classes for Pages
# ============================================================================

class PageTranslation(models.Model):
    """Stores translations of Page slugs and titles according to Language
    object.  
    """
    language = models.ForeignKey(Language, related_name='+')
    slug = models.CharField(max_length=SLUG_LENGTH)
    title = models.CharField(max_length=25, blank=True, null=True)

    page_data = models.ForeignKey(PageData)

    class Meta:
        app_label = 'yacon'

    @classmethod
    def create_translations(cls, page_data, translations):
        """Creates multiple PageTranslation objects based on a dictionary
        mapping Language objects to either tuples of (slug, title) or just to
        slug strings.

        @param page_data: page_data to create the translations for
        @param translations: dictionary of Language objects mapped to (slug,
            title) or slug strings, a PageTranslation is created for each of
            these mappings
        """

        for lang in translations.keys():
            thing = translations[lang]
            if type(thing) == tuple:
                (slug, title) = thing
            else:
                slug = thing
                title = None

            tx = PageTranslation(language=lang, slug=slug, title=title,
                page_data=page_data)
            tx.save()


class BlockTranslation(models.Model):
    """A Page object can have multiple copies of a Block each associated with a
    different Language.  To accomodate this, the ManyToMany relationship
    between Page objects and Block objects is done through a BlockTranslation.
    """
    page_data = models.ForeignKey(PageData)
    block = models.ForeignKey(Block)
    language = models.ForeignKey(Language)

    class Meta:
        app_label = 'yacon'
