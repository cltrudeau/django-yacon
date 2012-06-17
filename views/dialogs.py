# yacon.views.dialogs.py
# blame ctrudeau chr(64) arsensa.com
#
# Dialog box ajax methods for the nexus control panel.
#

import logging, json, urllib
from collections import OrderedDict

from django.db import IntegrityError
from django.conf import settings
from django.http import Http404, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from yacon.models.common import Language
from yacon.models.hierarchy import (Node, BadSlug, NodeTranslation, Menu,
    Menu, MenuItem, MenuItemTranslation)
from yacon.models.site import Site
from yacon.models.pages import MetaPage, Page, PageType, Translation

logger = logging.getLogger(__name__)

# ============================================================================
# Helpers
# ============================================================================

def _pages_subtree_as_list(node, language, depth=1):
    """Returns a string representation as <li> and <ul> tags of the node 
    passed in and its children."""
    space = depth * '    '
    output = []

    if node.name == None:
        output.append('%s<li><i>empty translation (%s)</i></li>' % (space,
            language.code))
    else:
        output.append('%s<li>%s at %s</li>' % (space, node.name, 
            node.node_to_path()))

    if node.has_children():
        output.append('%s<ul>' % space)
        for child in node.get_children():
            output.append( _pages_subtree_as_list(child, language, depth+1))

        output.append('%s</ul>' % space)

    # leaf node, check for pages
    metapages = MetaPage.objects.filter(node=node)
    if len(metapages) != 0:
        output.append('%s<ul>' % space)
        for metapage in metapages:
            for page in metapage.get_translations():
                output.append('    %s<li>"%s" (<i>%s</i>)</li>' % \
                    (space, page.title, page.language.code))

        output.append('%s</ul>' % space)

    return '\n'.join(output)


def _menu_subtree_as_list(item, depth=1):
    """Returns a string representation as <li> and <ul> tags of the menuitem 
    passed in and its children."""
    space = depth * '    '
    output = []

    default = item.get_default_translation()
    translations = item.get_translations(ignore_default=True)

    if default:
        name = '%s (%s)' % (default.name, default.language.code)
    else:
        name = '<i>empty translation (%s)</i>' % \
            item.menu.site.default_language.code

    tx_names = []
    for tx in translations:
        tx_names.append('%s (%s)' % (tx.name, tx.language.code))

    txs = ''
    if translations:
        txs = ' [%s]' % ', '.join(tx_names)

    output.append('%s<li>%s%s</li>' % (space, name, txs))

    if item.has_children():
        output.append('%s<ul>' % space)
        for child in item.get_children():
            output.append( _menu_subtree_as_list(child, depth+1))

        output.append('%s</ul>' % space)

    return '\n'.join(output)


def page_as_li(page):
    return '   <li>"%s" at %s (%s)</li>' % (page.title, page.uri, 
        page.language.code)


def reachable_aliases(metapages, language=None):
    """Returns a string containing an html <ul> list of any aliased pages
    reachable from the "metapages" passed in.
    """
    aliases = MetaPage.objects.filter(alias__in=metapages)
    alias_list = []
    if len(aliases) != 0:
        alias_list.append('<ul>')
        for metapage in aliases:
            for page in metapage.get_translations():
                if language == None:
                    # return all languages
                    alias_list.append(page_as_li(page))
                else:
                    # return only languages that match what was passed in
                    if page.language == language:
                        alias_list.append(page_as_li(page))

        alias_list.append('</ul>')
    return '\n'.join(alias_list)


def reachable_from_node(node, language=None, include_aliases=True):
    """Returns a tuple of strings containing html <ul> lists of the Nodes and
    pages that are children of "node" and any MetaPages associated with these
    items.  

    :params node: node to find reachables for
    :params language: if None, returns all items, if specified restricts list
        to just those with the given language, defaults to None
    :params include_aliases: False to skip calculation of aliases, returns
        None for second item in tuple

    :returns: (node_list, alias_list)
    """
    alias_list = None
    if include_aliases:
        # find all of the MetaPages that would be unreachable
        nodes = list(node.get_descendants())
        nodes.append(node)
        metapages = MetaPage.objects.filter(node__in=nodes)

        # find anything that aliases one of the targeted metapages
        alias_list = reachable_aliases(metapages, language)

    node_list = \
"""<ul>
%s
</ul>""" % _pages_subtree_as_list(node, node.site.default_language)

    return (node_list, alias_list)

# ============================================================================
# Site Dialog Methods
# ============================================================================

def missing_site_languages(request, site_id):
    """Returns a JSON hash of languages in the system but not in the given
    site."""
    site = get_object_or_404(Site, id=site_id)
    data = {}

    all_langs = set(Language.objects.all())
    site_langs = set([site.default_language, ])
    site_langs.update(site.alternate_language.all().order_by('identifier'))
    for lang in all_langs.difference(site_langs):
        data[lang.identifier] = lang.name

    return HttpResponse(json.dumps(data), content_type='application/json')


def site_languages(request, site_id):
    """Returns a JSON hash of languages for the given site."""
    site = get_object_or_404(Site, id=site_id)
    data = OrderedDict()

    langs = [site.default_language, ]
    langs.extend(site.alternate_language.all().order_by('identifier'))
    for lang in langs:
        data[lang.identifier] = lang.name

    return HttpResponse(json.dumps(data), content_type='application/json')


def all_languages(request):
    data = OrderedDict()
    langs = Language.objects.all().order_by('identifier')
    for lang in langs:
        data[lang.identifier] = lang.name

    return HttpResponse(json.dumps(data), content_type='application/json')

# ============================================================================
# Node Toolbar Dialog Box Methods
# ============================================================================

def remove_folder_warn(request, node_id):
    """Ajax call that returns a listing of the nodes and pages that would be
    effected if node with id "node_id" is deleted."""
    node = get_object_or_404(Node, id=node_id)

    # find all of the MetaPages that would be removed
    (nodes, aliases) = reachable_from_node(node)
    data = {
        'nodes':nodes,
        'aliases':aliases,
    }

    return render_to_response('nexus/ajax/remove_folder_warning.html', data,
        context_instance=RequestContext(request))


def remove_folder(request, node_id):
    """Deletes node with id "node_id" and all of its children.  Unlinks any
    aliases to removed items."""
    node = get_object_or_404(Node, id=node_id)
    node.delete()

    return HttpResponse()


def add_folder(request, node_id, title, slug):
    """Adds a new node underneath the given one."""
    node = get_object_or_404(Node, id=node_id)
    title = urllib.unquote(title)
    slug = urllib.unquote(slug)
    data = {}
    try:
        child = node.create_child(title, slug)
        data['key'] = 'node:%s' % child.id,
    except BadSlug, e:
        data['error'] = e.message
        
    return HttpResponse(json.dumps(data), content_type='application/json')


def add_page(request, node_id, page_type_id, title, slug):
    """Adds a new page underneath the given node."""
    node = get_object_or_404(Node, id=node_id)
    page_type = get_object_or_404(PageType, id=page_type_id)
    title = urllib.unquote(title)
    slug = urllib.unquote(slug)

    data = {}
    try:
        MetaPage.create_page(node, page_type, title, slug, {})
    except BadSlug, e:
        data['error'] = e.message
        
    return HttpResponse(json.dumps(data), content_type='application/json')


def add_path(request, node_id, lang, name, slug):
    """Adds a translation path to the given Node."""
    node = get_object_or_404(Node, id=node_id)
    name = urllib.unquote(name)
    slug = urllib.unquote(slug)

    data = {}
    try:
        langs = node.site.get_languages(lang)
        if len(langs) == 0:
            raise ValueError('Bad language selected')

        NodeTranslation.objects.create(node=node, slug=slug, name=name, 
            language=langs[0])
    except BadSlug, e:
        data['error'] = e.message
    except ValueError, e:
        data['error'] = e.message
        
    return HttpResponse(json.dumps(data), content_type='application/json')

# ============================================================================
# MetaPage Toolbar Dialog Box Methods
# ============================================================================

def remove_page_warn(request, metapage_id):
    """Ajax call that returns a listing of the translated pages that would be
    effected if metapage with id "metapage_id" is deleted."""
    metapage = get_object_or_404(MetaPage, id=metapage_id)

    # find all of the Pages that would be removed
    pages = Page.objects.filter(metapage=metapage)
    page_list = ['<ul>']
    for page in pages:
        page_list.append(page_as_li(page))
    page_list.append('</ul>')

    # find anything that aliases the targeted metapage
    alias_list = reachable_aliases([metapage, ])

    data = {
        'metapage':metapage,
        'pages':'\n'.join(page_list),
        'aliases':alias_list,
    }

    return render_to_response('nexus/ajax/remove_page_warning.html', data,
        context_instance=RequestContext(request))


def remove_page(request, metapage_id):
    """Deletes metapage with id "metapage_id" and all of its pages.  Unlinks any
    aliases to removed items."""
    metapage = get_object_or_404(MetaPage, id=metapage_id)
    metapage.delete()

    return HttpResponse()


def add_translation(request, metapage_id, lang, title, slug):
    """Adds a translation to the given MetaPage."""
    metapage = get_object_or_404(MetaPage, id=metapage_id)
    title = urllib.unquote(title)
    slug = urllib.unquote(slug)

    data = {}
    try:
        langs = metapage.node.site.get_languages(lang)
        if len(langs) == 0:
            raise ValueError('Bad language selected')

        Page.objects.create(metapage=metapage, title=title, slug=slug,
            language=langs[0])
    except BadSlug, e:
        data['error'] = e.message
    except ValueError, e:
        data['error'] = e.message
        
    return HttpResponse(json.dumps(data), content_type='application/json')


def page_types(request):
    data = {}
    for page_type in PageType.objects.all():
        data[page_type.id] = page_type.name

    return HttpResponse(json.dumps(data), content_type='application/json')

# ============================================================================
# MenuItem Toolbar Dialog Box Methods
# ============================================================================

def add_menu(request, site_id, name):
    """Adds a new Menu."""
    site = get_object_or_404(Site, id=site_id)
    name = urllib.unquote(name)

    data = {}
    Menu.objects.create(name=name, site=site)
    return HttpResponse()


def add_menuitem_translation(request, menuitem_id, lang, name):
    """Adds a translation to the given MetaPage."""
    menuitem = get_object_or_404(MenuItem, id=menuitem_id)
    name = urllib.unquote(name)

    data = {}
    try:
        langs = menuitem.menu.site.get_languages(lang)
        if len(langs) == 0:
            raise ValueError('Bad language selected')

        MenuItemTranslation.objects.create(menuitem=menuitem, name=name,
            language=langs[0])
    except ValueError, e:
        data['error'] = e.message
        
    return HttpResponse(json.dumps(data), content_type='application/json')


def menu_listing(request, metapage_id):
    """Returns a list of the menus for the site."""
    metapage = get_object_or_404(MetaPage, id=metapage_id)
    data = {}

    for menu in Menu.objects.filter(site=metapage.node.site):
        data[menu.id] = menu.name

    return HttpResponse(json.dumps(data), content_type='application/json')


def add_menuitem(request, menu_id, metapage_id, name):
    """Adds a new menuitem to the given menu."""
    menu = get_object_or_404(Menu, id=menu_id)
    metapage = get_object_or_404(MetaPage, id=metapage_id)
    name = urllib.unquote(name)

    lang = menu.site.default_language
    menu.create_child(metapage=metapage, translations={lang:name})
        
    return HttpResponse()

# ============================================================================
# Inline Action Dialog Methods
# ============================================================================

def remove_path_warn(request, translation_id):
    """Ajax call that returns a listing of the nodes and pages that would be
    effected if translation with id "translation_id" is changed."""
    translation = get_object_or_404(NodeTranslation, id=translation_id)

    (nodes, aliases) = reachable_from_node(translation.node,
        translation.language, include_aliases=False)

    data = {
        'path':translation.get_path(),
        'nodes':nodes,
    }

    return render_to_response('nexus/ajax/remove_path_warning.html', data,
        context_instance=RequestContext(request))


def remove_path(request, translation_id):
    translation = get_object_or_404(NodeTranslation, id=translation_id)
    translation.delete()
    return HttpResponse()


def edit_path_warn(request, translation_id):
    """Ajax call that returns a listing of the nodes and pages that would be
    effected if translation with id "translation_id" is changed."""
    translation = get_object_or_404(NodeTranslation, id=translation_id)

    (nodes, aliases) = reachable_from_node(translation.node,
        translation.language, include_aliases=False)

    data = {
        'path':translation.get_path(),
        'nodes':nodes,
    }

    return render_to_response('nexus/ajax/edit_path_warning.html', data,
        context_instance=RequestContext(request))


def edit_path(request, translation_id, name, slug):
    translation = get_object_or_404(NodeTranslation, id=translation_id)
    slug = urllib.unquote(slug)
    name = urllib.unquote(name)

    translation.slug = slug
    translation.name = name
    translation.save()
    return HttpResponse()


def make_default_metapage(request, metapage_id):
    """Sets the given metapage to be the default page for its parent node."""
    metapage = get_object_or_404(MetaPage, id=metapage_id)
    metapage.make_default_for_node()

    return HttpResponse()


def remove_page_translation(request, page_id):
    """Deletes page with id "page_id"."""
    page = get_object_or_404(Page, id=page_id)
    page.delete()

    return HttpResponse()


def remove_menuitem_translation(request, tx_id):
    """Deletes menu item translation with id "tx_id". """
    tx = get_object_or_404(MenuItemTranslation, id=tx_id)
    tx.delete()

    return HttpResponse()


def remove_menu_warn(request, menu_id):
    """Ajax call that returns a listing of the menuitems that would be
    effected if menu with id "menu_id" is removed.  """
    menu = get_object_or_404(Menu, id=menu_id)

    items = []
    for menuitem in menu.first_level.all():
        items.append(_menu_subtree_as_list(menuitem, 0))

    items_string = '<ul>\n%s\n</ul>' % '\n'.join(items)

    data = {
        'menu':menu,
        'items': items_string,
    }

    return render_to_response('nexus/ajax/remove_menu_warning.html', data,
        context_instance=RequestContext(request))


def remove_menuitem_warn(request, menuitem_id):
    """Ajax call that returns a listing of the menuitems that would be
    effected if menuitem with id "menuitem_id" is removed.  """
    menuitem = get_object_or_404(MenuItem, id=menuitem_id)

    items = _menu_subtree_as_list(menuitem, 0)
    items_string = '<ul>\n%s\n</ul>' % items

    data = {
        'menuitem':menuitem,
        'items': items_string,
    }

    return render_to_response('nexus/ajax/remove_menuitem_warning.html', data,
        context_instance=RequestContext(request))


def remove_menuitem(request, menuitem_id):
    """Deletes menu item with id "menuitem_id". """
    menuitem = get_object_or_404(MenuItem, id=menuitem_id)
    menuitem.delete()

    return HttpResponse()


def remove_menu(request, menu_id):
    """Deletes menu with id "menu_id". """
    menu = get_object_or_404(Menu, id=menu_id)
    menu.delete()

    return HttpResponse()

# ============================================================================
# Site Management Methods
# ============================================================================

def add_site_lang(request, site_id, identifier):
    site = get_object_or_404(Site, id=site_id)
    identifier = urllib.unquote(identifier)

    try:
        language = Language.objects.get(identifier=identifier)
        site.alternate_language.add(language)
    except Language.DoesNotExist:
        # only an ajax call, this dies and nothing happens anyhow
        pass

    return HttpResponse()


def add_site(request, name, domain, lang_identifier):
    name = urllib.unquote(name)
    domain = urllib.unquote(domain)
    lang_identifier = urllib.unquote(lang_identifier)
    data = {}

    try:
        language = Language.objects.get(identifier=lang_identifier)
        site = Site.create_site(name, domain, [language, ])
    except Language.DoesNotExist:
        # only an ajax call, this dies and nothing happens anyhow
        data['error'] = 'Problem occurred with language code'
    except IntegrityError, e:
        if 'Key (name)' in e.message:
            data['error'] = 'Site with name "%s" already exists' % name
        elif 'Key (domain)' in e.message:
            data['error'] = 'Site for domain "%s" already exists' % domain
        else:
            data['error'] = 'An error occurred.  The database reported %s' % \
                e.message

    return HttpResponse(json.dumps(data), content_type='application/json')


def edit_site(request, site_id, name, domain, lang_identifier):
    site = get_object_or_404(Site, id=site_id)
    name = urllib.unquote(name)
    domain = urllib.unquote(domain)
    lang_identifier = urllib.unquote(lang_identifier)

    data = {}
    try:
        language = Language.objects.get(identifier=lang_identifier)
        site.set_default_language(language)

        site.name = name
        site.domain = domain
        site.save()
    except Language.DoesNotExist:
        # only an ajax call, this dies and nothing happens anyhow
        data['error'] = 'Problem occurred with language code'
    except IntegrityError, e:
        if 'Key (name)' in e.message:
            data['error'] = 'Site with name "%s" already exists' % name
        elif 'Key (domain)' in e.message:
            data['error'] = 'Site for domain "%s" already exists' % domain
        else:
            data['error'] = 'An error occurred.  The database reported %s' % \
                e.message

    return HttpResponse(json.dumps(data), content_type='application/json')
