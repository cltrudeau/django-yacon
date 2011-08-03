# yacon.models.hierarchy.py
# blame ctrudeau chr(64) arsensa.com

import re, exceptions, logging

from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404
from django.db.models import Q

from treebeard.mp_tree import MP_Node

logger = logging.getLogger(__name__)

match_word = re.compile('^\w*$')
match_slash = re.compile('/')

# ============================================================================
# Exceptions
# ============================================================================

class PathNotFound(exceptions.Exception):
    pass


class BadSlug(exceptions.Exception):
    pass

# ============================================================================
# Utility Classes
# ============================================================================

class ParsedPath():
    def __init__(self, *args, **kwargs):
        self.slugs_in_path = []
        self.slugs_after_node = []
        self.path = ''
        self.language = ''
        self.node = None

    def __str__(self):
        return \
        'ParsedPath(path=%s, slugs_in_path=%s, slugs_after_node=%s, node=%s)' \
            % (self.path, self.slugs_in_path, self.slugs_after_node, self.node)

# ============================================================================
# Site Management
# ============================================================================

class Site(models.Model):
    """A Site object is the highest level container in the CMS.  It groups
    together pages, menus and associated configuration.
    """
    name = models.CharField(max_length=25, unique=True)
    doc_root = models.ForeignKey('yacon.Node', blank=True, null=True, 
        related_name='+')
    menus = models.ManyToManyField('yacon.Node', blank=True, null=True,
        related_name='+')

    class Meta:
        app_label = 'yacon'

    # --------------------------------------------
    # Factory/Fetch Methods
    @classmethod
    def create_site(cls, name, base_url, languages=[], config={}):
        """Creates a Site object with corresponding SiteURL and SiteConfig
        entries.

        @param name -- name of site
        @param base_url -- url this site is responsible for
        @param languages -- a list of language identifiers that are valid
            languages for this site.  First in the list is considered the
            default language.  If this list is empty then the
            settings.LANGUAGE_CODE is used as the default.  Note that
            languages are stored as config objects, sending in both a
            languages list and a config dict with "language" values may result
            in unpredictable behaviour.
        @param config -- optional dictionary which is converted into
            name/value pairs as SiteConfig entries

        @returns -- Site object
        """

        # create the Site object
        site = Site(name=name)
        site.save()

        # set the default language for the site -- has to be done before
        # creating the doc_root as the Node needs to know its language
        if len(languages) == 0:
            languages = [settings.LANGUAGE_CODE]

        sc = SiteConfig(site=site, name='default_language', 
            value=languages[0])
        sc.save()

        # set any remaining languages
        for lang in languages[1:]:
            sc = SiteConfig(site=site, name='language', value=lang)
            sc.save()

        site.create_doc_root()
        url = SiteURL(site=site, base_url=base_url)
        url.save()
        for name in config.keys():
            sc = SiteConfig(site=site, name=name, value=config[name])
            sc.save()

        return site

    @classmethod
    def get_site(cls, request):
        """Uses the domain information from an HttpRequest object to find the
        corresponding site or raises a 404 if no matching site found"""
        domain = request.META['HTTP_HOST']
        logger.debug('using domain "%s"' % domain)
        site_url = get_object_or_404(SiteURL, base_url=domain)
        site = site_url.site
        logger.debug('found site %s (id=%d)' % (site.name, site.id))

        return site

    def create_doc_root(self):
        if self.doc_root != None:
            raise AttributeError('There can be only one Site.doc_root at ' +\
                'a time.')

        self.doc_root = Node.add_root(site=self)
        self.save()
        tx = NodeTranslation(node=self.doc_root, name='root', slug='/',
            language=self.get_default_language())
        tx.save()

    # --------------------------------------------
    # Config Management

    def add_config(self, name, value):
        """Adds a SiteConfig name/value pair to this site

        @param name -- name of config to add
        @param value -- value of config to hold
        """
        config = SiteConfig(site=self, name=name, value=value)
        config.save()

    def get_config(self, name):
        """Returns a list of values for the given config name

        @param name -- name of config items to retrieve

        @returns -- list of values, or empty list if no matching names
        """
        configs = SiteConfig.objects.filter(site=self, name=name)
        values = configs.values_list('value', flat=True)

        return list(values)

    # --------------------------------------------
    # Multilingual Routines

    def get_languages(self, language_code=None):
        """Returns a list of language identifiers supported by this site.
        Language identifiers come in two forms: language_code (e.g. "en") and
        language_code-country (e.g. "en-GB").  If a language_code is passed in
        only those language identifiers who match the language_code will be
        returned.  

        List is source out of the SiteConfig table with keys matching
        "default_language" and "language".

        @param language_code -- restricts languages returned to just those who
            have a matching language_code
        @returns -- list of strings which are the language codes for this
            site.  List may be empty if there are no matching codes
        """
        configs = SiteConfig.objects.filter(Q(site=self),
            Q(name='default_language')|Q(name='language'))

        if language_code != None:
            configs = configs.filter(value__startswith=language_code)

        langs = []
        for config in configs:
            langs.append(config.value)

        return langs

    def get_default_language(self):
        """Returns the default language for this site."""
        config = SiteConfig.objects.get(site=self, name='default_language')
        return config.value

    # -----------------------------------------------------------------------
    # Search Methods

    def node_lang_from_path(self, path):
        """A path of slugs is used to uniquely identify a Node in the document
        hierarchy, this method walks a given path to return a tuple consisting
        of a Node object and the language of the path that resulted in
        returning the Node.

        For example, '/blogs/health/milk' will return the Node object
        corresponding to 'milk' (which is a child of health which is a child
        of blogs) along with the language 'en'.  

        As consistency of path language is not required, each level of the
        path can in theory be aliases in other languages.  The language
        returned is technically the language of the last portion of the path.

        @param path -- path portion of a URI for the desired Node.  Leading
            and trailing slashes are optional and ignored
        @raise PathNotFound -- if the path passed in doesn't correspond to the
            hierarchy
        @return -- (Node, language)
        """

        node = self.doc_root
        language = ''
        parts = match_slash.split(path)
        for part in parts:
            if part == '':
                continue 

            kids = node.get_children()
            found = False
            for kid in kids:
                if kid.has_slug(part):
                    found = True
                    language = kid.language_of_slug(part)
                    node = kid
                    break

            if not found:
                raise PathNotFound('%s has no child %s' % (node.slug, part))

        # if you get here succesfully then node is the last piece
        return (node, language)

    def node_from_path(self, path):
        """Calls node_lang_from_path, ignoring the language and returning just
        the Node

        @returns: Node object for the path
        """

        (node, lang) = self.node_lang_from_path(path)
        return node

    def parse_path(self, path):
        """Returns a ParsedPath object by walking the path given until it
        runs out of either tree or the path.  The ParsedPath object contains
        the list of slugs in the path and any slugs after the path (i.e. if we
        run out of tree) along with a Node object.  If the path does not
        result in finding a node then a ParsedPath object is still returned

        @param path: path to walk to find a container Node 
        @returns: ParsedPath object.
            ParsedPath.slugs_in_path: a list of slugs in the path passed in
            ParsedPath.language: language of slug where Node object is found.
                In theory the language should be the same for all slugs, but
                in practice this isn't enforced
            ParsedPath.slugs_after_node: a list of slugs found in the path
                after we ran out of tree to walk
            ParsedPath.Node: the Node object corresponding to the part of
                the tree where we ran out of path.  If the path does not
                correspond to the tree then Node will be None and all slugs in
                the path will be in ParsedPath.slugs_after_node"""

        node = self.doc_root
        parsed = ParsedPath()
        parsed.path = path
        parts = match_slash.split(path)
        end_of_tree = False
        for part in parts:
            if part == '':
                continue 

            if not end_of_tree:
                kids = node.get_children()
                found = False
                for kid in kids:
                    if kid.slug == part:
                        found = True
                        parsed.slugs_in_path.append(part)
                        parsed.node = kid
                        node = kid
                        break

                if not found:
                    parsed.slugs_after_node.append(part)
                    end_of_tree = True
            else:
                parsed.slugs_after_node.append(part)

        if len(parsed.slugs_in_path) > 0:
            last = parsed.slugs_in_path[-1]
            parsed.language = parsed.node.language_of_slug(last)
        return parsed


class SiteURL(models.Model):
    """Defines the URLs that are associated with a Site"""

    site = models.ForeignKey(Site)
    base_url = models.CharField(max_length=100, unique=True)

    class Meta:
        app_label = 'yacon'


class SiteConfig(models.Model):
    """A name/value pair object for configuring a site"""

    site = models.ForeignKey(Site)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    class Meta:
        app_label = 'yacon'

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
    site = models.ForeignKey(Site)
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
        language identifier strings mapped to name/slug tuples can be used to
        populate other translations.

        @param name: name of Node in default language
        @param slug: slug for Node in default language
        @param translations: dictionary mapping language codes to tuples of
            name/slug pairs to be used to populate translations.  Example:
            {'en-GB':('Colour','colour'), 'fr':('Couleur', 'couleur'), }

        @returns: newly created child Node

        @raise BadSlug: if the slug contains any non-alpha-numeric character
            or exceeds 25 characters in length
        """
        translations[self.site.get_default_language()] = (name, slug, )

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
        """Returns the name for this Node in the given language.  If no
        language is passed in then the Site's default language is used.  

        @param langauge: optional parameter specifying the language to return
            the Node's name in.  If not given the Site's default language is
            used

        @returns: string containing desired Node name
        """
        if language == None:
            language = self.site.get_default_language()

        tx = NodeTranslation.objects.get(node=self, language=language)
        return tx.name

    def get_slug(self, language=None):
        """Returns the slug for this Node in the given language.  If no
        language is passed in then the Site's default language is used.  

        @param langauge: optional parameter specifying the language to return
            the Node's slug in.  If not given the Site's default language is
            used

        @returns: string containing desired Node slug
        """
        if language == None:
            language = self.site.get_default_language()

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
        """Returns the language code of the NodeTranslation object that
        contains the given slug

        @param find_slug: slug to find the language code for
        @returns: string with langauge code in it
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

        @param language: optional parameter specifying the language to express
            the path in.  If none specified then Site object's default
            language is used
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
    """Stores translations of Node names and slugs according to language.  The
    language should be a language identifier as specified in 

    http://www.i18nguy.com/unicode/language-identifiers.html
    """
    language = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    slug = models.CharField(max_length=25)
    node = models.ForeignKey(Node)

    class Meta:
        app_label = 'yacon'
