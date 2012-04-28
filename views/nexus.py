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
from yacon.models.hierarchy import Node, BadSlug
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
    default_lang = node.site.default_language.code
    if node.name == None:
        name = '<i>empty translation (%s)</i>' % default_lang

    node_hash = {
        'title': name,
        'key': 'node:%d' % node.id,
        'icon': 'fatcow/folder.png',
        'expand': True,
    }

    if node.has_children():
        children = []
        for child in node.get_children():
            subtree = _build_subtree(child)
            children.append(subtree)

        node_hash['children'] = children

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
                title = '<i>empty translation (%s)</i>' % default_lang
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

    return node_hash


def _build_subtree_as_list(node, depth=1):
    """Returns a string representation as <li> and <ul> tags of the node 
    passed in and its children."""
    space = depth * '    '
    default_lang = node.site.default_language.code
    output = []

    if node.name == None:
        output.append('%s<li><i>empty translation (%s)</i></li>' % (space,
            default_lang))
    else:
        output.append('%s<li>%s at %s</li>' % (space, node.name, 
            node.node_to_path()))

    if node.has_children():
        output.append('%s<ul>' % space)
        for child in node.get_children():
            output.append( _build_subtree_as_list(child, depth+1))

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
            node.site.default_language.code
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


def full_tree_default_site(request):
    # pick the first site and return it
    sites = Site.objects.all()
    if len(sites) == 0:
        return HttpResponse(json.dumps([]), content_type='application/json')

    return full_tree(request, sites[0].id)


def remove_folder_warn(request, node_id):
    """Ajax call that returns a listing of the nodes and pages that would be
    effected if node with id "node_id" is deleted."""
    node = get_object_or_404(Node, id=node_id)

    # find all of the MetaPages that would be removed
    nodes = list(node.get_descendants())
    nodes.append(node)
    metapages = MetaPage.objects.filter(node__in=nodes)

    # find anything that aliases one of the targeted metapages
    aliases = MetaPage.objects.filter(alias__in=metapages)
    alias_list = []
    if len(aliases) != 0:
        alias_list.append('<ul>')
        for metapage in aliases:
            for page in metapage.get_translations():
                alias_list.append('   <li>"%s" at %s (%s)</li>' % (page.title,
                    page.uri, page.language.code))

        alias_list.append('</ul>')

    data = {
        'nodes':\
"""<ul>
%s
</ul>""" % _build_subtree_as_list(node),
        'aliases':'\n'.join(alias_list),
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
    data = {}
    try:
        child = node.create_child(title, slug)
        data['key'] = 'node:%s' % child.id,
    except BadSlug, e:
        data['error'] = e.message
        
    return HttpResponse(json.dumps(data), content_type='application/json')
