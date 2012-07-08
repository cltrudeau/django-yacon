# yacon.views.left_control.py
# blame ctrudeau chr(64) arsensa.com
#
# Left pane of Nexus control panel.  Contains Site drop-down and the site
# tree.
#

import logging, json

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from yacon.decorators import superuser_required
from yacon.models.hierarchy import Node, Menu, MenuItem, MenuItemTranslation
from yacon.models.site import Site
from yacon.models.pages import MetaPage

logger = logging.getLogger(__name__)

# ============================================================================
# Tree Building Methods
# ============================================================================

def _pages_subtree(node, language, is_root, depth_limit):
    """Returns a hash representation in dynatree format of the node passed in
    and its children."""
    name = '%s (%s)' % (node.name, node.slug)
    if node.name == None:
        name = '<i>empty translation (%s)</i>' % language.code

    node_hash = {
        'title': name,
        'key': 'node:%d' % node.id,
        'icon': 'fatcow/folder.png',
    }
    if is_root:
        node_hash['expand'] = True

    if depth_limit == 0:
        # reached as far as we're going to go, just check for kids
        count = MetaPage.objects.filter(node=node).count()
        if count != 0 or node.has_children():
            node_hash['isLazy'] = True

        return node_hash

    # check for pages at this level
    metapages = MetaPage.objects.filter(node=node)
    if len(metapages) != 0:
        children = []
        for metapage in metapages:
            icon = "fatcow/page_white.png"
            if metapage.is_alias():
                icon = "fatcow/page_white_link.png"
            page = metapage.get_default_translation()
            if page == None:
                title = '<i>empty translation (%s)</i>' % language.code
            else:
                title = page.title

            page_hash = {
                'title': title,
                'key': 'metapage:%d' % metapage.id,
                'icon': icon,
            }
            children.append(page_hash)

        if 'children' in node_hash:
            node_hash['children'].extend(children)
        else:
            node_hash['children'] = children

    # process any children of this level
    if node.has_children():
        children = []
        for child in node.get_children():
            dl = depth_limit
            if dl != -1:
                dl = dl - 1
            subtree = _pages_subtree(child, language, False, dl)
            children.append(subtree)

        if 'children' in node_hash:
            node_hash['children'].extend(children)
        else:
            node_hash['children'] = children

    return node_hash


def _menuitem_subtree(menuitem, language, is_root, depth_limit):
    """Returns a hash representation in dynatree format of the menuitem passed
    in and its children."""
    try:
        tx = MenuItemTranslation.objects.get(menuitem=menuitem, 
            language=language)
        name = tx.name
    except MenuItemTranslation.DoesNotExist:
        name = '<i>empty translation (%s)</i>' % language.code

    menuitem_node = {
        'title': name,
        'key': 'menuitem:%d' % menuitem.id,
    }
    if is_root:
        menuitem_node['expand'] = True

    if depth_limit == 0:
        # reached as far as we're going to go, check for kids
        if menuitem.has_children():
            menuitem_node['isLazy'] = True
            menuitem_node['icon'] = 'fatcow/folder.png'

        return menuitem_node

    if menuitem.has_children():
        children = []
        for child in menuitem.get_children():
            dl = depth_limit
            if depth_limit != -1:
                dl -= 1
            subtree = _menuitem_subtree(child, language, False, dl)
            children.append(subtree)

        menuitem_node['icon'] = 'fatcow/folder.png'
        menuitem_node['children'] = children

    return menuitem_node


def _build_dynatree(site):
    """Returns a dynatree hash representation of our pages and menu
    hierarchy."""
    subtree = _pages_subtree(site.doc_root, site.default_language, True, 1)
    subtree['activate'] = True
    pages_node = {
        'title': 'Pages',
        'key': 'system:pages',
        'expand': True,
        'icon': 'fatcow/folders_explorer.png',
        'children': [subtree, ],
    }

    language = site.default_language
    menus = []
    for menu in Menu.objects.filter(site=site):
        items = []
        for item in menu.first_level.all():
            items.append(_menuitem_subtree(item, language, True, 1))

        menus.append({
            'title': menu.name,
            'key': 'menu:%d' % menu.id,
            'expand': True,
            'icon': 'fatcow/folders.png',
            'children':items,
        })

    menus_node = {
        'title': 'Menus',
        'key': 'system:menus',
        'expand': True,
        'icon': 'fatcow/folders_explorer.png',
        'children': menus,
    }

    tree = [pages_node, menus_node]
    return tree

# ============================================================================
# Control Panel: Site Methods
# ============================================================================

@superuser_required
def get_sites(request):
    sites = Site.objects.all().order_by('id')
    data = {}
    for site in sites:
        data[site.id] = site.name

    return HttpResponse(json.dumps(data), content_type='application/json')

# ============================================================================
# Control Panel: Tree Methods
# ============================================================================

@superuser_required
def full_tree(request, site_id):
    site = get_object_or_404(Site, id=site_id)
    tree = _build_dynatree(site)

    print tree
    return HttpResponse(json.dumps(tree), content_type='application/json')


@superuser_required
def full_tree_default_site(request):
    # pick the first site and return it
    sites = Site.objects.all()
    if len(sites) == 0:
        return HttpResponse(json.dumps([]), content_type='application/json')

    return full_tree(request, sites[0].id)


@superuser_required
def sub_tree(request):
    key = request.GET.get('key')
    if not key:
        raise Http404('no key sent')

    (node_type, node_id) = key.split(':')
    if not node_type or not node_id:
        raise Http404('bad key sent: "%s"' % key)

    if node_type == 'node':
        node = get_object_or_404(Node, id=node_id)
        tree = _pages_subtree(node, node.site.default_language, False, 1)
        subtree = tree['children']
    elif node_type == 'menuitem':
        menuitem = get_object_or_404(MenuItem, id=node_id)
        tree = _menuitem_subtree(menuitem, menuitem.menu.site.default_language, 
            False, 1)
        subtree = tree['children']
    else:
        raise Http404('bad node_type sent: "%s"' % node_type)

    return HttpResponse(json.dumps(subtree), content_type='application/json')
