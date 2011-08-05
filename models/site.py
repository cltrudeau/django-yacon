# yacon.models.hierarchy.py
# blame ctrudeau chr(64) arsensa.com

import re, exceptions, logging

from django.db import models
from django.shortcuts import get_object_or_404
from django.db.models import Q

from yacon.models.language import Language
from yacon.models.hierarchy import Node, NodeTranslation

logger = logging.getLogger(__name__)

match_slash = re.compile('/')

# ============================================================================
# Exceptions
# ============================================================================

class PathNotFound(exceptions.Exception):
    pass

# ============================================================================
# Utility Classes
# ============================================================================

class ParsedPath():
    def __init__(self, *args, **kwargs):
        self.slugs_in_path = []
        self.slugs_after_node = []
        self.path = ''
        self.language = None
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
    default_language = models.ForeignKey(Language, related_name='+')
    alternate_language = models.ManyToManyField(Language, related_name='+')

    class Meta:
        app_label = 'yacon'

    # --------------------------------------------
    # Factory/Fetch Methods
    @classmethod
    def create_site(cls, name, base_url, languages=[], config={}):
        """Creates a Site object with corresponding SiteURL and SiteConfig
        entries.

        @param name -- name of site
        @param base_url -- url that this site is responsible for
        @param languages -- a list of Language objects that will be the
            allowed languages for this site.   First item in the list is
            treated as the default language for the site.  If no list is given
            then Languages.default_language() is used to determine the sites
            default language.
        @param config -- optional dictionary which is converted into
            name/value pairs as SiteConfig entries

        @returns -- Site object
        """
        default_language = None
        if len(languages) == 0:
            default_language = Language.default_language()
        else:
            default_language = languages.pop(0)

        # create the Site object
        site = Site(name=name, default_language=default_language)
        site.save()

        # set any remaining languages
        for lang in languages:
            site.alternate_language.add(lang)

        # create the root of the document hierarchy and the base url
        site.create_doc_root()
        url = SiteURL(site=site, base_url=base_url)
        url.save()

        # for any config passed in create the corresponding objects
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
        """Creates the document root Node for the site.  The default Language
        is used for this Node; as the Node itself contains '/' as the slug,
        the language is more or less moot.  The name of the node should only
        ever show up in admin areas
        """
        if self.doc_root != None:
            raise AttributeError('There can be only one Site.doc_root at ' +\
                'a time.')

        self.doc_root = Node.add_root(site=self)
        self.save()
        tx = NodeTranslation(node=self.doc_root, name='root', slug='/',
            language=self.default_language)
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
        """Returns a list of Language objects supported by this site.

        @param language_code -- restricts languages returned to just those who
            have a matching language_code
        @returns -- list of strings which are the language codes for this
            site.  List may be empty if there are no matching codes
        """
        langs = []

        df = self.default_language
        if language_code == None:
            langs.append(df)
            langs.extend(self.alternate_language.all())
        else:
            if df.identifier.lower().startswith(language_code.lower()):
                langs.append(df)

            langs.extend(self.alternate_language.filter(
                identifier__istartswith=language_code))

        return langs

    # -----------------------------------------------------------------------
    # Search Methods

    def node_lang_from_path(self, path):
        """A path of slugs is used to uniquely identify a Node in the document
        hierarchy, this method walks a given path to return a tuple consisting
        of Node and Language object for the Node at the end of the given path.

        For example, '/blogs/health/milk' will return the Node object
        corresponding to 'milk' (which is a child of health which is a child
        of blogs) along with the Language object containing 'en'.  

        As consistency of path language is not required, each level of the
        path can in theory be aliases in other languages.  The language
        returned is technically the Language of the last portion of the path.

        @param path -- path portion of a URI for the desired Node.  Leading
            and trailing slashes are optional and ignored
        @raise PathNotFound -- if the path passed in doesn't correspond to the
            hierarchy
        @return -- (Node, Language)
        """

        node = self.doc_root
        language = None
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
            ParsedPath.language: Language object for the slug where Node object 
                is found.  In theory the Language should be the same for all
                slugs, but in practice this isn't enforced
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
