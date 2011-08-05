# yacon.models.hierarchy.py
# blame ctrudeau chr(64) arsensa.com

import re, exceptions, logging

from django.db import models
from treebeard.mp_tree import MP_Node
from yacon.models.language import Language

logger = logging.getLogger(__name__)

match_word = re.compile('^\w*$')
match_slash = re.compile('/')

# ============================================================================
# Exceptions
# ============================================================================

class BadSlug(exceptions.Exception):
    pass

# ============================================================================
# Hierarchy Management
# ============================================================================

class Node(MP_Node):
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
    default_page = models.ForeignKey('yacon.Page', blank=True, null=True,
        related_name='+')

    class Meta:
        app_label = 'yacon'

    def __unicode__(self):
        return 'Node: %s (%s)' % (self.name, self.slug)

    # -----------------------------------------------------------------------
    # Factory/Fetch Methods
    def create_child(self, name, slug, translations={}):
        """Creates a Node object as a child of this Node.  Name and slug for
        the default language are passed in.  An optional dictionary of
        Language objects mapped to name/slug tuples can be used to
        populate other translations.

        @param name: name of Node in default language
        @param slug: slug for Node in default language
        @param translations: dictionary mapping language codes to tuples of
            name/slug pairs to be used to populate translations.  Example:
            {Language('en-GB'):('Colour','colour'), Language('fr'):('Couleur', 
            'couleur'), }

        @returns: newly created child Node

        @raise BadSlug: if the slug contains any non-alpha-numeric character
            or exceeds 25 characters in length
        """
        translations[self.site.default_language] = (name, slug)

        # check for bad slugs
        for key, value in translations.items():
            (name, slug) = value

            if len(slug) > 25:
                raise BadSlug('Maximum slug length is 25 characters')

            if not match_word.search(slug):
                raise BadSlug('Slug must be of form [0-9a-zA-Z_]*')

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

    def get_name(self, language=None):
        """Returns the name for this Node in the given Language.  If no
        Language is passed in then the Site's default Language is used.  

        @param langauge: optional parameter specifying the Language to return
            the Node's name in.  If not given the Site's default Language is
            used

        @returns: string containing desired Node name
        """
        if language == None:
            language = self.site.default_language

        tx = NodeTranslation.objects.get(node=self, language=language)
        return tx.name

    def get_slug(self, language=None):
        """Returns the slug for this Node in the given Language.  If no
        Language is passed in then the Site's default language is used.  

        @param langauge: optional parameter specifying the Language to return
            the Node's slug in.  If not given the Site's default Language is
            used

        @returns: string containing desired Node slug
        """
        if language == None:
            language = self.site.default_language

        tx = NodeTranslation.objects.get(node=self, language=language)
        return tx.slug

    def has_slug(self, find_slug):
        """Returns true if one of the NodeTranslation for this Node contains
        the given slug.

        @param find_slug: slug to search for
        @returns: True if find_slug matches one of the slug translations
        """

        txs = NodeTranslation.objects.filter(node=self, slug=find_slug)
        return len(txs) > 0

    def language_of_slug(self, find_slug):
        """Returns the Language object in the NodeTranslation object that
        contains the given slug

        @param find_slug: slug to find the Language for
        @returns: Language object
        """
        tx = NodeTranslation.objects.get(node=self, slug=find_slug)
        return tx.language

    # -----------------------------------------------------------------------
    # Tree Walking Methods

    def _walk_tree_to_string(self, node, output, indent):
        """Breadth first walk of tree returning node as string

        @param node -- node to walk
        @param string -- string to append to before returning
        @param output -- list of lines containing a string from each node
            visited
        @param indent -- how much to indent the displayed node
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

        @param language: optional parameter specifying the Language to express
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
        return '/%s/' % '/'.join([n.get_slug(language) for n in nodes]) 

    def has_children(self):
        return self.get_children_count() > 0


class NodeTranslation(models.Model):
    """Stores translations of Node names and slugs according to Language
    object.  
    """
    language = models.ForeignKey(Language, related_name='+')
    name = models.CharField(max_length=30)
    slug = models.CharField(max_length=25)
    node = models.ForeignKey(Node)

    class Meta:
        app_label = 'yacon'
