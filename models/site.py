# yacon.models.hierarchy.py
# blame ctrudeau chr(64) arsensa.com

import re, exceptions, logging

from django.db import models
from django.shortcuts import get_object_or_404

from yacon.models.language import Language
from yacon.models.pages import PageTranslation
from yacon.models.hierarchy import Node, NodeTranslation

logger = logging.getLogger(__name__)

match_slash = re.compile('/')

# ============================================================================
# Utility Classes
# ============================================================================

class ParsedPath(object):
    """Temporary object representing a URI path that has been parsed into a
    series of slugs.  

    :param path: path that was parsed
    :param slugs_in_path: a list of slugs in the path passed in
    :param slugs_after_item: a list of slugs found in the path
        after we ran out of tree to walk
    :param language: Language object for the slug where final item
        object is found.  In theory the Language should be the same 
        for all slugs, but in practice this isn't enforced
    :param node: if the end of the path walked is a Node then this
        will contain that Node object
    :param pagetranslation: if the end of the path walked is a translated 
        page or a Node with a default_page setting then this will contain the
        corresponding PageTranslation object
    :param item_type: one of:
        * UNKNOWN: if walking the path did not result in a page or Node
        * NODE: if walking the path resulted in a Node
        * PAGETRANSLATION: if the walking the path resulted in a page
            or a Node with a default_page setting
    """
    UNKNOWN = 0
    NODE = 1
    PAGETRANSLATION = 2
    ITEM_TYPES = {
        UNKNOWN:'Unknown',
        NODE:'Node',
        PAGETRANSLATION:'PageTranslation',
    }

    def __init__(self, *args, **kwargs):
        self.slugs_in_path = []
        self.slugs_after_item = []
        self.path = ''
        self.language = None
        self.node = None
        self.page = None
        self.item_type = ParsedPath.UNKNOWN

    def __str__(self):
        return 'ParsedPath(path=%s, slugs_in_path=%s, slugs_after_item=%s, '\
            'item_type=%s, node=%s, page=%s)' % (self.path, self.slugs_in_path, 
            self.slugs_after_item, self.ITEM_TYPES[self.item_type], self.node, 
            self.page)

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

        :param name -- name of site
        :param base_url -- url that this site is responsible for
        :param languages -- a list of Language objects that will be the
            allowed languages for this site.   First item in the list is
            treated as the default language for the site.  If no list is given
            then Languages.default_language() is used to determine the sites
            default language.
        :param config -- optional dictionary which is converted into
            name/value pairs as SiteConfig entries

        :returns: Site object
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

        :param name -- name of config to add
        :param value -- value of config to hold
        """
        config = SiteConfig(site=self, name=name, value=value)
        config.save()

    def get_config(self, name):
        """Returns a list of values for the given config name

        :param name -- name of config items to retrieve

        :returns: list of values, or empty list if no matching names
        """
        configs = SiteConfig.objects.filter(site=self, name=name)
        values = configs.values_list('value', flat=True)

        return list(values)

    # --------------------------------------------
    # Multilingual Routines

    def get_languages(self, language_code=None):
        """Returns a list of Language objects supported by this site.

        :param language_code -- restricts languages returned to just those who
            have a matching language_code

        :returns: list of strings which are the language codes for this
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

    def parse_path(self, path):
        """A path of slugs is used to uniquely identify a Node or page in the
        document hierarchy, this method walks a given path until it runs out
        of either tree or the path, generating a ParsedPath object along the
        way.  The ParsedPath object contains the list of slugs in the path,
        any slugs after the path (i.e. if we run out of tree) and a resulting
        Node or PageTranslation object that corresponds to the path.  If the
        path does not result in finding a Node or page then a ParsedPath
        object is still returned.  

        As consistency of path language is not required, each level of the
        path can in theory be aliased in other languages.  The language
        returned is technically the Language of the last portion of the path,
        i.e. of either the last Node or PageTranslation found.

        If a Node object has a default_page setting and the path indicates the
        Node, then both a Node and PageTranslation object are returned, but 
        the item_type will indicate a PageTranslation.

        :param path: path to walk to find a container Node 

        :returns: ParsedPath object.
        """
        node = self.doc_root
        parsed = ParsedPath()
        parsed.path = path
        parts = match_slash.split(path)
        found_end_node = False
        # step through the parts of the path looking for Node objects
        for part in parts:
            # if the path contained double slashes, ignore them
            if part == '':
                continue 

            if not found_end_node:
                # search the children of this Node for the slug we've parsed
                kids = list(node.get_children())
                nts = NodeTranslation.objects.filter(slug=part, node__in=kids)
                if len(nts) > 0:
                    # found slugs -- there should only be one, but to play it
                    # safe we don't enforce that
                    if len(nts) > 1:
                        logger.warning('Multiple slugs matched for children '
                            + 'of node=%s' % node + ' and slug=%s' % part)

                    parsed.slugs_in_path.append(part)
                    parsed.node = nts[0].node
                    parsed.item_type = ParsedPath.NODE
                    node = nts[0].node
                else:
                    parsed.slugs_after_item.append(part)
                    found_end_node = True
            else:
                # already found leaf Node, all slugs after this get stored
                parsed.slugs_after_item.append(part)

        if parsed.item_type == ParsedPath.UNKNOWN:
            # didn't find a Node in the path, return what we've built
            return parsed

        # if you get here then we found a Node, check for pages and default
        # pages 
        if len(parsed.slugs_after_item) > 0:
            # there are still slugs left after we found the last Node, see if
            # there is a page for it
            pt = PageTranslation.find(parsed.node, parsed.slugs_after_item)
            if pt != None:
                parsed.pagetranslation = pt
                parsed.language = pt.language
                parsed.item_type = ParsedPath.PAGETRANSLATION

        # either there were no slugs after we found the Node, or there
        # were and there was no page for it; so we're only a Node, check
        # for default page for this Node
        if parsed.item_type == ParsedPath.NODE:
            # find the language of the Node so we can check for a default page
            last = parsed.slugs_in_path[-1]
            parsed.language = parsed.node.language_of_slug(last)

            # get the default page
            pt = parsed.node.get_default_pagetranslation(parsed.language)
            if pt != None:
                # Node has a default_page
                parsed.item_type = ParsedPath.PAGETRANSLATION
                parsed.pagetranslation = pt

        return parsed

    def find_pagetranslation(self, uri):
        """Returns a PageTranslation object corresponding to the given URI.
        The URI can either be a path to a PageTranslation or to a Node with a
        default page.  If it is neither then None is returned.

        :param uri: URI corresponding to a path to a PageTranslation or Node
            with a default page

        :returns: PageTranslation object or None
        """
        parsed = self.parse_path('/' + uri)
        if parsed.item_type == ParsedPath.PAGETRANSLATION:
            return parsed.pagetranslation

        # If you get here, then either: 1) URI was invalid, 2) URI was for a
        # Node without a default_page
        return None
            

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
