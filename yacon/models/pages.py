# yacon.models.pages.py
import logging, json

from django.contrib.auth.models import User
from django.db import models, IntegrityError, transaction
from django.shortcuts import render

from yacon import conf
from yacon.definitions import (SLUG_LENGTH, TITLE_LENGTH, ALLOWED_TAGS,
    ALLOWED_ATTRIBUTES, ALLOWED_STYLES)
from yacon.loaders import dynamic_load
from yacon.models.common import Language, TimeTrackedModel, PagePermissionTypes
from yacon.sanitizer import SanitizedTextField

logger = logging.getLogger(__name__)

# ============================================================================
# Tag Management
# ============================================================================

class DuplicateTagException(Exception):
    pass


class Tag(TimeTrackedModel):
    site = models.ForeignKey('yacon.Site')

    class Meta:
        app_label = 'yacon'

    @classmethod
    def factory(cls, site, translations):
        """Creates a Tag and its associated TagTranslation objects.

        :param translation: dictionary mapping languages to tag text
        """
        with transaction.atomic():
            tag = Tag.objects.create(site=site)
            for lang, text in translations.items():
                num = TagTranslation.objects.filter(language=lang,
                    text=text).count()
                if num:
                    raise DuplicateTagException('%s exists already for %s' % (
                        text, lang.code))

                TagTranslation.objects.create(tag=tag, language=lang,
                    text=text)

        return tag

    def __unicode__(self):
        return 'Tag(id=%s)' % self.id

    def display_text(self, language=None):
        if not language:
            language = self.site.default_language

        try:
            tx = TagTranslation.objects.get(tag=self, language=language)
            return tx.text
        except TagTranslation.DoesNotExist:
            return None

    def get_default_translation(self):
        """Returns the TagTranslation object in the site's default language or
        None.
        """
        try:
            return TagTranslation.objects.get(tag=self,
                language=self.site.default_language)
        except TagTranslation.DoesNotExist:
            return None

    def get_translations(self, ignore_default=False):
        """Returns a list of TagTranslations for this tag.  

        :param ignore_default: [optional] if set to True the returned list
            will not include the translation for the site's default language.
            Defaults to False.

        :returns: list of TagTranslation objects
        """
        try:
            txs = TagTranslation.objects.filter(tag=self)
            if ignore_default:
                txs = txs.exclude(language=self.site.default_language)

            return txs

        except TagTranslation.DoesNotExist:
            return []

    @property
    def has_missing_translations(self):
        """Returns True if there are languages in the site that don't have a
        translated version of this tag."""
        txs = TagTranslation.objects.filter(tag=self).count()
        langs = self.site.language_count()

        return txs != langs


class TagTranslation(TimeTrackedModel):
    tag = models.ForeignKey(Tag)
    language = models.ForeignKey(Language, related_name='+')
    text = models.CharField(max_length=30)

    class Meta:
        app_label = 'yacon'

    def __unicode__(self):
        return 'Tag(id=%s, %s:%s)' % (self.id, self.language.code, self.text)

# ============================================================================
# Page Management Classes
# ============================================================================

class PageType(TimeTrackedModel):
    """Defines how a page is constructed, tied to a template for rendering."""
    name = models.CharField(max_length=25, unique=True)
    template = models.CharField(max_length=50, blank=True)
    dynamic = models.CharField(max_length=100, blank=True)
    block_types = models.ManyToManyField('yacon.BlockType')

    class Meta:
        app_label = 'yacon'

    def __unicode__(self):
        return 'PageType(%s)' % self.name

    def render(self, request, data):
        # if there is something in template, do a static render
        if self.template:
            return render(request, self.template, data)

        # dynamic content render, call the function that is registered to
        # return a response
        fn = dynamic_load(self.dynamic)
        response = fn(request, data)
        return response


class BadContentHandler(Exception):
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
            return self.content_handler_instance

        # instantiate a content handler
        try:
            mod = __import__(self.module_name, globals(), locals(),
                [self.content_handler_name])
        except Exception as e:
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
            klass = getattr(mod, self.content_handler_name)
            logger.debug('found class for content handler')
        except Exception as e:
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
            self.content_handler_instance = klass(self, parms)
        except Exception as e:
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

        return self.content_handler_instance


class Block(TimeTrackedModel):
    """Defines a block of content for the CMS"""
    block_type = models.ForeignKey(BlockType)

    parameters = models.TextField(null=True, blank=True)
    content = SanitizedTextField(allowed_attributes=ALLOWED_ATTRIBUTES,
        allowed_tags=ALLOWED_TAGS, allowed_styles=ALLOWED_STYLES)

    # management of owner, groups, privileges etc. should go here (?)

    def __init__(self, *args, **kwargs):
        super(Block, self).__init__(*args, **kwargs)
        self.is_editable = False

    def __unicode__(self):
        return u'Block(block_type=%s, content=%s)' % (self.block_type,
            self.content)

    class Meta:
        app_label = 'yacon'

    def render(self, request, context):
        """Returns a rendered version of the block via its ContentHandler"""

        handler = self.block_type.get_content_handler()
        return handler.render(request, context, self)

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
    title = models.CharField(max_length=TITLE_LENGTH, blank=True, null=True)

    metapage = models.ForeignKey('yacon.MetaPage')

    # content for the page is stored in a series of blocks
    blocks = models.ManyToManyField(Block)

    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)
        self.after_slugs = None
        self.metapage_alias = None

    class Meta:
        app_label = 'yacon'
        unique_together = ('slug', 'metapage')

    def __unicode__(self):
        return 'Page(id=%s, path=%s)' % (self.id, self.uri)

    def save(self, *args, **kwargs):
        # ensure slug is unique at all times
        suffix = ''
        i = 2
        while(True):
            try:
                save_id = transaction.savepoint()
                self.slug += suffix
                super(Page, self).save(*args, **kwargs)
                break
            except IntegrityError:
                transaction.savepoint_rollback(save_id)
                suffix = '-%d' % i
                i += 1

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

    @classmethod
    def find_by_page_type(cls, page_type, language=None, owner=None):
        """Returns all of the pages for the given page_type.  If the language
        parameter is provided then the results are restricted to just that
        language.

        :param page_type: returns pages that have this PageType object
        :param language: [optional] language to restrict the search by
        :param owner: [optional] user to restrict search by

        :returns: list of Page objects
        """
        pages = []
        kwargs = {
            'metapage___page_type':page_type
        }
        if language:
            kwargs['language'] = language
        if owner:
            kwargs['metapage__owner'] = owner

        pages = Page.objects.filter(**kwargs)
        return pages

    @classmethod
    def find_by_tag(cls, language, tag_text):
        """Returns all of the pages with the given tag text

        :param language: Language of the tag text and page
        :param tag_text: tag text to look for

        :returns: list of Pages
        """
        try:
            tx = TagTranslation.objects.get(language=language, text=tag_text)
            return Page.objects.filter(metapage__tags=tx.tag,
                language=language)
        except TagTranslation.DoesNotExist:
            return []

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

        if conf.site.multisite:
            return '//%s%s%s' % (self.metapage.node.site.domain, node_part, 
                self.slug)

        # single site, use a relative url
        return '%s%s' % (node_part, self.slug)

    @property
    def lang_code(self):
        return self.language.identifier.upper()

    @property
    def all_blocks(self):
        """Shortcut property method for "blocks.all()" so it can be called
        inside of a template."""
        return self.blocks.all()

    @property
    def last_updated(self):
        """Returns the most recent time stamp of this Page and all of its
        associated blocks."""
        latest = self.updated
        for block in self.blocks.all():
            if block.updated > latest:
                latest = block.updated

        return latest

    def tag_translations(self):
        """Returns a list of TagTranslation objects for this Page."""
        txs = []
        for tag in self.metapage.tags.all():
            try:
                tx = TagTranslation.objects.get(tag=tag, language=self.language)
                txs.append(tx)
            except TagTranslation.DoesNotExist:
                # no translation, ignore
                pass

        return txs


class DoubleAliasException(Exception):
    pass


class MetaPage(TimeTrackedModel):
    """This class represents a collection of translated pages in the CMS along
    with its placement in the document hierarchy.  All pages, even if they
    only have one translation, have a MetaPage.
    """
    node = models.ForeignKey('yacon.Node')
    _page_type = models.ForeignKey(PageType, blank=True, null=True)
    alias = models.ForeignKey('yacon.MetaPage', blank=True, null=True)
    is_node_default = models.BooleanField(default=False)

    owner = models.ForeignKey(User, null=True)
    permission = models.CharField(max_length=3, 
        choices=list(PagePermissionTypes),
        default=PagePermissionTypes.INHERIT)
    hidden = models.BooleanField(default=False)

    tags = models.ManyToManyField(Tag)

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
    def create_page(cls, node, page_type, title, slug, block_hash, owner=None,
            auto_slug=False, permission=PagePermissionTypes.INHERIT,
            hidden=False):
        """Creates, saves and returns a MetaPage object with a corresponding 
        Page object in the Site default language.

        :param node: node in Site hierarchy where the page lives
        :param page_type: PageType for this Page
        :param title: title for the page
        :param slug: slug for the page
        :param block_hash: hash of content mapping block_type to content
        :param owner: [optional] owner of the page being created
        :param auto_slug: [optional, default=False] True will automatically
            fix a slug that does not match the uniqueness property.  False
            raises an exception
        :param permission: [optional, default=Inherit] access permissions of
            page
        :param hidden: [optional, default=False] if this page is hidden from
            view

        :returns: MetaPage object
        """
        translation = Translation(language=node.site.default_language,
            title=title, slug=slug, block_hash=block_hash)
        return cls.create_translated_page(node, page_type, [translation],
            owner, auto_slug, permission=permission, hidden=hidden)

    @classmethod
    def create_translated_page(cls, node, page_type, translations, owner=None,
            auto_slug=False, permission=PagePermissionTypes.INHERIT, 
            hidden=False):
        """Creates, saves and returns a MetaPage object with multiple
        Page object translations.

        :param node: node in Site hierarchy where the page lives
        :param page_type: PageType for this Page
        :param translations: a list of Translation objects
        :param owner: [optional] owner of the pages being created
        :param auto_slug: [optional, default=False] True will automatically
            fix a slug that does not match the uniqueness property.  False
            raises an exception
        :param permission: [optional, default=Inherit] access permissions of
            page
        :param hidden: [optional, default=False] if this page is hidden from
            view

        :returns: MetaPage object

        :raises: BadSlug, if any of the slugs are not valid
        """
        # create the MetaPage
        metapage = MetaPage(node=node, _page_type=page_type, owner=owner,
            permission=permission, hidden=hidden)
        metapage.save()

        # make sure no duplicates in Translations -- would like to enforce
        # this at the database level but django is blowing up when trying to
        # use unique_together here
        langs = [tx.language for tx in translations]
        unique = set(langs)
        if len(langs) != len(unique):
            raise AttributeError('Two translations had the same language')

        for tx in translations:
            slug = node.validate_slug(tx.slug, auto_slug)
            page = Page.objects.create(metapage=metapage, title=tx.title, 
                slug=slug, language=tx.language)

            # add the content to the translation
            for key, value in tx.block_hash.items():
                block = Block.objects.create(block_type=key, content=value)
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
    # Setters
    def make_default_for_node(self):
        # find any other nodes that are marked as default and unset them
        mps = MetaPage.objects.filter(node=self.node, is_node_default=True)
        for mp in mps:
            mp.is_node_default = False
            mp.save()

        self.is_node_default = True
        self.save()

    # -------------------------------------------
    # Getters
    @property
    def default_title(self):
        """Returns the title of the Page for this MetaPage in the default
        translation, or None if there is no such Page."""
        default_page = self.get_default_translation()
        if default_page:
            return default_page.title

        return None

    @property
    def effective_permission(self):
        """Returns the effective permission for this MetaPage.  It is one of
        either the permission attribute, or if that is INHERIT, then it
        returns the effective permsission of our node."""
        if self.permission != PagePermissionTypes.INHERIT:
            return self.permission

        # inherit means we get our permission from our node
        return self.node.effective_permission

    @property
    def permission_string(self):
        return PagePermissionTypes.get_value(self.permission)

    @property
    def effective_permission_string(self):
        return PagePermissionTypes.get_value(self.effective_permission)

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

    @property
    def has_alias(self):
        aliases = MetaPage.objects.filter(alias=self)
        return len(aliases) != 0

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

    @property
    def has_missing_translations(self):
        """Returns True if there are languages in the site that there are no
        pages for."""
        return self.page_set.count() != self.node.site.language_count()
