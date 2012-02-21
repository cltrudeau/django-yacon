# yacon.views.nexus.py
# blame ctrudeau chr(64) arsensa.com
#
# Nexus is the area for administrators to control the contents of the site,
# permissions, user management etc.  Not named the obvious "admin" to avoid
# conflicts with Django's admin features
#

import logging

from django.http import Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from yacon.utils import quote, unquote
from yacon.models.hierarchy import Node
from yacon.models.site import Site
from yacon.models.pages import MetaPage, Page

logger = logging.getLogger(__name__)

# ============================================================================
# Generic Page Display Views
# ============================================================================

def _tree_to_html_list(node, output, indent):
    spacer = 3 * (indent + 1) * ' '
    output.append( spacer + '   <li>' +\
        '<img src="/static/icons/fatcow/folder.png">&nbsp;' +\
        '<a class="obj_info" href="/yacon/nexus/ajax_node_info' +\
        '/%d/">%s (%s)<a/>' % (node.id, node.name, node.slug) + '</li>')
    
    default_lang = node.site.default_language
    if node.has_children():
        output.append('%s<ul>' % spacer)
        for child in node.get_children():
            _tree_to_html_list(child, output, indent+1)
        output.append('%s</ul>' % spacer)
    else: 
        # leaf node, check for pages
        metapages = MetaPage.objects.filter(node=node)
        if len(metapages) != 0:
            output.append('%s<ul class="content_list">' % spacer)
            for metapage in metapages:
                page = metapage.get_default_translation()
                image = "/static/icons/fatcow/page_white.png"
                if metapage.is_alias():
                    image = "/static/icons/fatcow/page_white_link.png"

                # output the list item for the primary language
                uri = quote(page.get_uri())
                output.append(spacer + '   <li>' +\
                    '<img src="%s">&nbsp;<a class="obj_info" ' % image +\
                    'href="/yacon/nexus/ajax_page_info/?uri=%s">%s</a>' \
                    % (uri, page.title))

                for tx in page.other_translations():
                    uri = quote(tx.get_uri())
                    output.append('(<a class="obj_info" href="' +\
                        '/yacon/nexus/ajax_page_info/?uri=%s/">%s</a>)' \
                        % (uri, tx.language.identifier.upper()))

                output.append('</li>')
            output.append('%s</ul>' % spacer)


def content_listing(request):
    """Renders a hierarchical list of all the sites and corresponding content 
    pages in the system"""
    sites = Site.objects.all()

    output = []
    for site in sites:
        output.append('<h3>Site: %s</h3>' % site.name)
        output.append('<ul class="content_list">')
        _tree_to_html_list(site.doc_root, output, 0)
        output.append('</ul>')

    data = {}
    data['title'] = 'Content Listing'
    data['tree'] = "\n".join(output)

    return render_to_response('nexus/content_list.html', data, 
        context_instance=RequestContext(request))


def _construct_page_info(request, uri):
    link = unquote(uri)
    site = Site.get_site(request)
    page = site.find_page(link)
    if page == None:
        raise Http404

    data = {}
    data['title'] = 'Page Info'
    data['page'] = page

    data['metapage'] = page.metapage
    data['is_alias'] = False
    if page.metapage_alias != None:
        data['metapage'] = page.metapage_alias
        data['is_alias'] = True

    data['blocks'] = page.blocks.all()
    data['uri'] = page.get_uri()

    #if page.is_alias():
    #    data['alias'] = page._alias.id

    return data

def page_info(request):
    data = _construct_page_info(request, request.GET['uri'])

    return render_to_response('nexus/page_info.html', data, 
        context_instance=RequestContext(request))

# ============================================================================
# Ajax Methods
# ============================================================================

def ajax_node_info(request, node_id):
    node = Node.objects.get(id=node_id)
    if node == None:
        return HttpResponse('')

    data = {}
    data['node'] = node
    data['num_metapages'] = len(MetaPage.objects.filter(node=node))
    data['num_children'] = node.get_children_count()

    # find all of the aliases for this page
    data['path_tuples'] = []
    langs = node.site.get_languages()
    for lang in langs:
        path = node.node_to_path(lang)
        page = None
        if node.default_metapage != None:
            page = node.default_metapage.get_translation(lang)

        data['path_tuples'].append((path, lang, page))

    return render_to_response('nexus/ajax/node_info.html', data, 
        context_instance=RequestContext(request))

def ajax_page_info(request):
    data = _construct_page_info(request, request.GET['uri'])

    return render_to_response('nexus/ajax/page_info.html', data, 
        context_instance=RequestContext(request))
