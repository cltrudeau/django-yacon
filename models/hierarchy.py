# yacon.models.hierarchy.py
# blame ctrudeau chr(64) arsensa.com

import re, exceptions, logging

from django.db import models
from treebeard.mp_tree import MP_Node
from yacon.models.common import Language, TimeTrackedModel
from yacon.models.pages import Page
from yacon.definitions import SLUG_LENGTH

logger = logging.getLogger(__name__)

MATCH_WORD = re.compile('^[-\w]*$')

# ============================================================================
# Exceptions
# ============================================================================

class BadSlug(exceptions.Exception):
    pass

# ============================================================================
# Hierarchy Management
# ============================================================================

class BaseNode(MP_Node, TimeTrackedModel):
    class Meta:
        abstract = True
        app_label = 'yacon'

    def has_children(self):
        return self.get_children_count() > 0


class Node(BaseNode):
    """A Site object represents a collection of page hiearchies and menus that
    are represented as a series of trees.  The Node object is a single node in
    one of those trees.

    Each node is identified by a slug with a series of slugs forming a path to
    an individual Node.  Slugs can be translated into multiple languages, thus
    allowing for multiple paths identifying a single unique Node.  A path
    should never point to two different Nodes in a single Site but as this is
    computationally expensive to enforce it is left to the developer to
    ensure.

    It is highly suggested that the factory methods be used to construct new
    Node objects.  There are two types of factory methods: those for creating
    root objects are on the Site class, those for creating children are on the
    Node class itself.  Node objects are based on django-treebeard's MP_Node
    object and any of those methods are available, but the factory methods
    attempt to abstract some of the associated complexity and enforce rules
    around formatting of slugs, etc.  
    """
    site = models.ForeignKey('yacon.Site')

    class Meta:
        app_label = 'yacon'

    def __unicode__(self):
        return 'Node: %s (%s)' % (self.name, self.slug)

    # -----------------------------------------------------------------------
    # Utility Methods
    def validate_slug(self, slug):
        """Raises a BadSlug exception if "slug" is not valid."""
        if len(slug) > SLUG_LENGTH:
            raise BadSlug('Maximum slug length is %d characters' % SLUG_LENGTH)

        if not MATCH_WORD.search(slug):
            raise BadSlug('Slug must be of form [0-9a-zA-Z_-]*')

        # find all children of this node and search their slugs
        slugmatches = NodeTranslation.objects.filter(slug=slug,
            node__in=self.get_children())
        if len(slugmatches) != 0:
            raise BadSlug('A child node already has the given slug')

        # now search for pages in this node with the same slug
        page = Page.find(self, [slug, ])
        if page != None:
            raise BadSlug('A page in this node already has the given slug.')

    # -----------------------------------------------------------------------
    # Factory/Fetch Methods
    def create_child(self, name, slug, translations={}):
        """Creates a Node object as a child of this Node.  Name and slug for
        the default language are passed in.  An optional dictionary of
        Language objects mapped to name/slug tuples can be used to
        populate other translations.

        :param name: name of Node in default language
        :param slug: slug for Node in default language
        :param translations: dictionary mapping language codes to tuples of
            name/slug pairs to be used to populate translations.  Example:
            {Language('en-GB'):('Colour','colour'), Language('fr'):('Couleur', 
            'couleur'), }

        :returns: newly created child Node

        :raises: BadSlug, if the slug contains any non-alpha-numeric
            character, exceeds 25 characters in length, or exists at this
            level already
        """
        translations[self.site.default_language] = (name, slug)
        children = self.get_children()

        # check for bad slugs
        for key, value in translations.items():
            (name, slug) = value
            self.validate_slug(slug)

        # no bad slugs, create the child node
        child = self.add_child(site=self.site)

        # add translations to child
        for key, value in translations.items():
            (name, slug) = value

            tx = NodeTranslation(node=child, language=key, name=name, slug=slug)
            tx.save()

        return child

    # -----------------------------------------------------------------------
    # Getter Methods
    @property 
    def name(self):
        """Returns the name for this Node in the Site's default translation"""
        return self.get_name()

    @property 
    def slug(self):
        """Returns the slug for this Node in the Site's default translation"""
        return self.get_slug()

    @property
    def has_missing_translations(self):
        """Returns True if there are languages in the site that there are no
        translations for in this node."""
        return self.nodetranslation_set.count() != self.site.language_count()

    @property
    def default_metapage(self):
        mps = self.metapage_set.filter(is_node_default=True)
        if len(mps) == 0:
            return None

        return mps[0]

    def get_default_page(self, language):
        """If this Node has an associated default MetaPage item return a
        translated Page for it in the given Language.  

        :param language: Language object to use for getting the Page, can be
            None to get the default language

        :returns: Page representing the default page for this Node, or None if
            there isn't one, or isn't one in the given language
        """
        if self.default_metapage == None:
            return None

        if language == None:
            # no language passed in, use default language
            return self.default_metapage.get_default_translation()

        return self.default_metapage.get_translation(language)

    def get_name(self, language=None):
        """Returns the name for this Node in the given Language.  If no
        Language is passed in then the Site's default Language is used.  

        :param langauge: optional parameter specifying the Language to return
            the Node's name in.  If not given the Site's default Language is
            used

        :returns: string containing desired Node name
        """
        if language == None:
            language = self.site.default_language

        try:
            tx = NodeTranslation.objects.get(node=self, language=language)
            return tx.name
        except NodeTranslation.DoesNotExist:
            return None

    def get_slug(self, language=None):
        """Returns the slug for this Node in the given Language.  If no
        Language is passed in then the Site's default language is used.  

        :param langauge: optional parameter specifying the Language to return
            the Node's slug in.  If not given the Site's default Language is
            used

        :returns: string containing desired Node slug
        """
        if language == None:
            language = self.site.default_language

        try:
            tx = NodeTranslation.objects.get(node=self, language=language)
            return tx.slug
        except NodeTranslation.DoesNotExist:
            return None

    def has_slug(self, find_slug):
        """Returns true if one of the NodeTranslation for this Node contains
        the given slug.

        :param find_slug: slug to search for

        :returns: True if find_slug matches one of the slug translations
        """

        txs = NodeTranslation.objects.filter(node=self, slug=find_slug)
        return len(txs) > 0

    def language_of_slug(self, find_slug):
        """Returns the Language object in the NodeTranslation object that
        contains the given slug

        :param find_slug: slug to find the Language for

        :returns: Language object
        """
        tx = NodeTranslation.objects.get(node=self, slug=find_slug)
        return tx.language

    # -----------------------------------------------------------------------
    # Tree Walking Methods

    def _walk_tree_to_string(self, node, output, indent):
        """Breadth first walk of tree returning node as string

        :param node -- node to walk
        :param string -- string to append to before returning
        :param output -- list of lines containing a string from each node
            visited
        :param indent -- how much to indent the displayed node
        """
        output.append('%s%s (%s)' % (3*indent*' ', node.name, node.slug))
        for child in node.get_children():
            self._walk_tree_to_string(child, output, indent+1)

    def tree_to_string(self):
        """Returns a string representation of the sub-tree using the 'self' 
        node as root"""

        output = []
        self._walk_tree_to_string(self, output, 0)
        return "\n".join(output)

    def node_to_path(self, language=None):
        """Returns a path string for this node

        :param language: optional parameter specifying the Language to express
            the path in.  If none specified then Site object's default
            Language is used
        """
        if self.is_root():
            return '/'

        nodes = []
        for node in self.get_ancestors():
            nodes.append(node)

        # get_ancestors() will include root which we don't use in paths and
        # won't include us, so remove the first and add this node at the end
        nodes.pop(0)
        nodes.append(self)
        path = '/'
        for node in nodes:
            slug = node.get_slug(language)
            if slug == None:
                return None

            path += slug + '/'
        return path


class NodeTranslation(TimeTrackedModel):
    """Stores translations of Node names and slugs according to Language
    object.  
    """
    language = models.ForeignKey(Language, related_name='+')
    name = models.CharField(max_length=30)
    slug = models.CharField(max_length=SLUG_LENGTH)
    node = models.ForeignKey(Node)

    class Meta:
        app_label = 'yacon'

    def get_path(self):
        return self.node.node_to_path(self.language)

# ============================================================================
# Menu Management

class MenuItem(BaseNode):
    """A MenuItem is a node in a hierarchy that is displayed to the user,
    typically for navigation, that is independent of the document hierarchy.
    A MenuItem can be "clickable" and associated with a Metapage, or not
    "clickable" and simply a placeholder in the hierarchy.  

    A Metapage is only allowed to be mapped to a single MenuItem across all
    menus.  This allows for easy determination from the URL as to where in the
    menu the user is.  If you want the same content to show up in two
    MenuItems then create a Metapage alias.
    """
    metapage = models.OneToOneField('yacon.MetaPage', blank=True, null=True,
        unique=True)
    menu = models.ForeignKey('yacon.Menu')

    class Meta:
        app_label = 'yacon'

    def __unicode__(self):
        return 'MenuItem(id=%s)' % self.id

    def create_child(self, metapage, translations={}):
        child = self.add_child(metapage=metapage, menu=self.menu)
        for key, value in translations.items():
            MenuItemTranslation.objects.create(language=key, name=value, 
                menuitem=child)
        return child

    # --------------------
    # Translation Access Methods
    def get_translation(self, language):
        """Returns a MenuItemTranslation object for this MenuItem in the given 
        language.

        :param language: Language for the corresponding translation

        :returns: MenuItemTranslation object or None
        """
        try:
            return MenuItemTranslation.objects.get(menuitem=self, 
                language=language)
        except MenuItemTranslation.DoesNotExist:
            return None

    def get_translations(self, ignore_default=False):
        """Returns a list of MenuItemTranslation objects representing the 
        for this MenuItem.

        :param ignore_default: if True the default language will not be
            returned in the list; defaults to False

        :returns: list of MenuItemTranslation objects
        """
        try:
            txs = MenuItemTranslation.objects.filter(menuitem=self)
            if ignore_default:
                txs = txs.exclude(language=self.menu.site.default_language)

            return txs

        except MenuItemTranslation.DoesNotExist:
            return None

    def get_default_translation(self):
        """Returns the MenuItemTranslation object for the site default language

        :returns: MenuItemTranslation object or None
        """
        try:
            return MenuItemTranslation.objects.get(menuitem=self, 
                language=self.menu.site.default_language)
        except MenuItemTranslation.DoesNotExist:
            return None

    @property
    def has_missing_translations(self):
        """Returns True if there are languages in the site that there are no
        translations for in this metapage."""
        txs = self.menuitemtranslation_set.count()
        langs = self.menu.site.language_count()
        print 'has_missing_tx tx: ', txs
        print 'has_missing_tx lang: ', langs

        return txs != langs

    @property
    def can_move_out(self):
        """Returns True if this item is not at root depth."""
        depth = self.get_depth() 
        return depth != 1

    @property
    def can_move_up(self):
        """Returns True if this item is not the first sibling."""
        first = self.get_first_sibling() 
        return first != self

    @property
    def can_move_down(self):
        """Returns True if this item is not the last sibling."""
        last = self.get_last_sibling() 
        return last != self


class Menu(TimeTrackedModel):
    """Represents a menu associated with a site.  The name in this menu is for
    configuration purposes only, the MenuItems contained within it (and their
    translations) are what are displayed to the user.
    """
    name = models.CharField(max_length=30)
    site = models.ForeignKey('yacon.Site')

    @property
    def first_level(self):
        return MenuItem.objects.filter(menu=self, depth=1)

    def create_child(self, metapage, translations={}):
        item = MenuItem.add_root(metapage=metapage, menu=self)
        for key, value in translations.items():
            MenuItemTranslation.objects.create(language=key, name=value, 
                menuitem=item)
        return item


class MenuItemTranslation(TimeTrackedModel):
    """Stores translations of MenuItem names according to Language object.  
    """
    language = models.ForeignKey(Language, related_name='+')
    name = models.CharField(max_length=30)
    menuitem = models.ForeignKey(MenuItem)

    class Meta:
        app_label = 'yacon'

    def __unicode__(self):
        return 'MenuItemTranslation: %s (%s)' % (self.name, self.language.code)

    @property 
    def page(self):
        """Returns the Page that corresponds to this language for the MetaPage
        that this item's menuitem points to.  Essentially, where this item
        points."""
        if hasattr(self, '_cached_page'):
            return self._cached_page

        self._cached_page = self.menuitem.metapage.get_translation(
            self.language)
        return self._cached_page
