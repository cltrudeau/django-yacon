# yacon.views.right_control.py
# blame ctrudeau chr(64) arsensa.com
#
# Right pane in Nexus control panel.  Shows the contents of items selected in
# the site tree in the left panel.

import logging, json, urllib
from collections import OrderedDict

from django.db import IntegrityError
from django.conf import settings
from django.http import Http404, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from yacon.models.common import Language
from yacon.models.hierarchy import (Node, BadSlug, NodeTranslation, Menu,
    MenuItem, MenuItemTranslation)
from yacon.models.site import Site
from yacon.models.pages import MetaPage, Page, PageType, Translation

logger = logging.getLogger(__name__)

# ============================================================================
# Control Panel: Site Info Button Methods
# ============================================================================

def site_info(request, site_id):
    site = get_object_or_404(Site, id=site_id)

    data = {
        'site':site,
        'alternate_languages':site.alternate_language.all(),
    }
    return render_to_response('nexus/ajax/site_info.html', data,
        context_instance=RequestContext(request))


# ============================================================================
# Control Panel: Node Selected Methods
# ============================================================================

def node_info(request, node_id):
    node = Node.objects.get(id=node_id)
    if node == None:
        return HttpResponse('')

    default_path = node.node_to_path(node.site.default_language)
    if default_path == None:
        default_path = '<i>empty translation (%s)</i>' % \
            node.site.default_language.code
    data = {
        'node':node,
        'num_metapages':len(MetaPage.objects.filter(node=node)),
        'num_children':node.get_children_count(),
        'path_items':[],
        'default_path':default_path,
    }

    class PathItem(object):
        pass

    # find all of the aliases for this page
    langs = node.site.get_languages()
    for lang in langs:
        item = PathItem()
        item.lang = lang
        item.path = node.node_to_path(lang)
        item.translation = None
        if item.path:
            try:
                item.translation = NodeTranslation.objects.get(node=node, 
                    language=lang)
            except NodeTranslation.DoesNotExist:
                # no translations available, e.g. root node, do nothing
                pass
        page = None
        if node.default_metapage != None:
            item.page = node.default_metapage.get_translation(lang)

        data['path_items'].append(item)

    return render_to_response('nexus/ajax/node_info.html', data, 
        context_instance=RequestContext(request))


def missing_node_translations(request, node_id):
    """Returns a JSON object hash of languages for which there are no
    translations in this Node."""
    node = get_object_or_404(Node, id=node_id)
    data = {}
    langs = [node.site.default_language, ]
    for lang in node.site.alternate_language.all():
        langs.append(lang)

    for translation in NodeTranslation.objects.filter(node=node):
        if translation.language in langs:
            langs.remove(translation.language)

    for lang in langs:
        data[lang.identifier] = lang.name

    return HttpResponse(json.dumps(data), content_type='application/json')


# ============================================================================
# Control Panel: MetaPage Selected Methods
# ============================================================================

def metapage_info(request, metapage_id):
    metapage = get_object_or_404(MetaPage, id=metapage_id)

    default_page = metapage.get_default_translation()
    translated_pages = metapage.get_translations(ignore_default=True)

    try:
        menuitem = metapage.menuitem
    except MenuItem.DoesNotExist:
        menuitem = None

    data = {
        'title':'MetaPage Info',
        'metapage':metapage,
        'default_page':default_page,
        'translated_pages':translated_pages,
        'menuitem':menuitem,
    }

    return render_to_response('nexus/ajax/metapage_info.html', data, 
        context_instance=RequestContext(request))


def missing_metapage_translations(request, metapage_id):
    """Returns a JSON object hash of languages for which there are no
    translations in this MetaPage."""
    metapage = get_object_or_404(MetaPage, id=metapage_id)
    data = {}
    langs = [metapage.node.site.default_language, ]
    for lang in metapage.node.site.alternate_language.all():
        langs.append(lang)

    for page in metapage.get_translations():
        if page.language in langs:
            langs.remove(page.language)

    for lang in langs:
        data[lang.identifier] = lang.name

    return HttpResponse(json.dumps(data), content_type='application/json')


# ============================================================================
# Control Panel: Menu Selected Methods
# ============================================================================

def menus_control(request):
    return render_to_response('nexus/ajax/menus_control.html', {}, 
        context_instance=RequestContext(request))


def menu_info(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)

    data = {
        'title':'Menu Info',
        'menu':menu,
    }

    return render_to_response('nexus/ajax/menu_info.html', data, 
        context_instance=RequestContext(request))


def move_menuitem_out(request, menuitem_id):
    menuitem = get_object_or_404(MenuItem, id=menuitem_id)
    try:
        parent = menuitem.get_parent()
        print 'menuitem: ', menuitem
        print 'parent: ', parent
        menuitem.move(parent, 'right')
    except:
        logger.exception('problem moving item out %s', menuitem_id)

    return HttpResponse()


def move_menuitem_up(request, menuitem_id):
    menuitem = get_object_or_404(MenuItem, id=menuitem_id)
    try:
        sibling = menuitem.get_prev_sibling()
        menuitem.move(sibling, 'left')
    except:
        logger.exception('problem moving item up %s', menuitem_id)

    return HttpResponse()


def move_menuitem_down(request, menuitem_id):
    menuitem = get_object_or_404(MenuItem, id=menuitem_id)
    try:
        sibling = menuitem.get_next_sibling()
        menuitem.move(sibling, 'right')
    except:
        logger.exception('problem moving item down %s', menuitem_id)

    return HttpResponse()

# ============================================================================
# Control Panel: MenuItem Selected Methods
# ============================================================================

def menuitem_info(request, menuitem_id):
    menuitem = get_object_or_404(MenuItem, id=menuitem_id)

    default_translation = menuitem.get_default_translation()
    translated_items = menuitem.get_translations(ignore_default=True)

    data = {
        'title':'MenuItem Info',
        'menuitem':menuitem,
        'default_translation':default_translation,
        'translated_items':translated_items,
    }

    return render_to_response('nexus/ajax/item_info.html', data, 
        context_instance=RequestContext(request))


def missing_menuitem_translations(request, menuitem_id):
    """Returns a JSON object hash of languages for which there are no
    translations in this MenuItem."""
    menuitem = get_object_or_404(MenuItem, id=menuitem_id)
    data = {}
    langs = [menuitem.menu.site.default_language, ]
    for lang in menuitem.menu.site.alternate_language.all():
        langs.append(lang)

    for translation in MenuItemTranslation.objects.filter(menuitem=menuitem):
        if translation.language in langs:
            langs.remove(translation.language)

    for lang in langs:
        data[lang.identifier] = lang.name

    return HttpResponse(json.dumps(data), content_type='application/json')
