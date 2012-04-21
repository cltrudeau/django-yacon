# yacon.views.nexus.py
# blame ctrudeau chr(64) arsensa.com
#
# Nexus is the area for administrators to control the contents of the site,
# permissions, user management etc.  Not named the obvious "admin" to avoid
# conflicts with Django's admin features
#

import logging, json

from django.http import Http404, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from yacon.utils import quote, unquote
from yacon.models.hierarchy import Node
from yacon.models.site import Site, SiteURL
from yacon.models.pages import MetaPage, Page

logger = logging.getLogger(__name__)

# ============================================================================
# Generic Page Display Views
# ============================================================================

def control_panel(request):
    data = {}
    data['title'] = 'Control Panel'

    return render_to_response('nexus/control_panel.html', data, 
        context_instance=RequestContext(request))

# ============================================================================
# Helpers
# ============================================================================

def _build_subtree(node):
    """Returns a hash representation in dynatree format of the node passed in
    and its children."""
    name = '%s (%s)' % (node.name, node.slug)
    if node.name == None:
        name = '<i>empty translation (%s)</i>' %\
            node.site.default_language.identifier

    node_hash = {
        'title': name,
        'key': 'node:%d' % node.id,
        'icon': 'fatcow/folder.png',
        'expand': True,
    }

    default_lang = node.site.default_language
    if node.has_children():
        children = []
        for child in node.get_children():
            subtree = _build_subtree(child)
            children.append(subtree)

        node_hash['children'] = children
    else: 
        # leaf node, check for pages
        metapages = MetaPage.objects.filter(node=node)
        if len(metapages) != 0:
            children = []
            for metapage in metapages:
                icon = "fatcow/page_white.png"
                if metapage.is_alias():
                    icon = "fatcow/page_white_link.png"
                page = metapage.get_default_translation()
                if page == None:
                    title = '<i>empty translation (%s)</i>' % \
                        node.site.default_language.identifier
                else:
                    title = page.title

                page_hash = {
                    'title': title,
                    'key': 'metapage:%d' % metapage.id,
                    'icon': icon,
                }
                children.append(page_hash)

            node_hash['children'] = children

    return node_hash


# ============================================================================
# Ajax Methods
# ============================================================================

def node_info(request, node_id):
    node = Node.objects.get(id=node_id)
    if node == None:
        return HttpResponse('')

    default_path = node.node_to_path(node.site.default_language)
    if default_path == None:
        default_path = '<i>empty translation (%s)</i>' % \
            node.site.default_language.identifier
    data = {
        'node':node,
        'num_metapages':len(MetaPage.objects.filter(node=node)),
        'num_children':node.get_children_count(),
        'path_tuples':[],
        'default_path':default_path,
    }

    # find all of the aliases for this page
    langs = node.site.get_languages()
    for lang in langs:
        path = node.node_to_path(lang)
        page = None
        if node.default_metapage != None:
            page = node.default_metapage.get_translation(lang)

        data['path_tuples'].append((path, lang, page))

    return render_to_response('nexus/ajax/node_info.html', data, 
        context_instance=RequestContext(request))


def metapage_info(request, metapage_id):
    metapage = get_object_or_404(MetaPage, id=metapage_id)

    default_page = metapage.get_default_translation()
    translated_pages = metapage.get_translations(ignore_default=True)

    data = {
        'title':'MetaPage Info',
        'metapage':metapage,
        'default_page':default_page,
        'translated_pages':translated_pages,
    }

    return render_to_response('nexus/ajax/metapage_info.html', data, 
        context_instance=RequestContext(request))


def get_sites(request):
    sites = Site.objects.all()
    data = {}
    for site in sites:
        data[site.id] = site.name

    return HttpResponse(json.dumps(data), content_type='application/json')


def site_info(request, site_id):
    site = get_object_or_404(Site, id=site_id)
    url = SiteURL.objects.get(site=site)

    data = {
        'site':site,
        'url':url.base_url,
        'alternate_languages':site.alternate_language.all(),
    }
    return render_to_response('nexus/ajax/site_info.html', data,
        context_instance=RequestContext(request))


def full_tree(request, site_id):
    site = get_object_or_404(Site, id=site_id)
    subtree = _build_subtree(site.doc_root)
    subtree['activate'] = True
    tree = [subtree, ]

    return HttpResponse(json.dumps(tree), content_type='application/json')
