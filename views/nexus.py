# yacon.views.nexus.py
# blame ctrudeau chr(64) arsensa.com
#
# Nexus is the area for administrators to control the contents of the site,
# permissions, user management etc.  Not named the obvious "admin" to avoid
# conflicts with Django's admin features
#

import logging

from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

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
        '<img src="/static/icons/fatcow/node-tree.png">&nbsp;' +\
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

                # output the list item for the primary language
                output.append(spacer + '   <li>' +\
                    '<img src="/static/icons/fatcow/page.png">&nbsp;' +\
                    '<a class="obj_info" ' + \
                    'href="/yacon/nexus/ajax_page_info/%d/">%s</a>' \
                    % (page.id, page.title))

                for tx in page.other_translations():
                    output.append('(<a class="obj_info" href="' +\
                        '/yacon/nexus/ajax_page_info/%d/">%s</a>)' \
                        % (tx.id, tx.language.identifier.upper()))

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


def _construct_page_info(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    data = {}
    data['title'] = 'Page Info'
    data['page'] = page
    data['blocks'] = page.blocks.all()
    data['uri'] = page.get_uri()

    #if page.is_alias():
    #    data['alias'] = page._alias.id

    return data

def page_info(request, page_id):
    data = _construct_page_info(request, page_id)

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
        print 'lang: ', lang
        path = node.node_to_path(lang)
        print 'path: ', path
        page = None
        if node.default_metapage != None:
            page = node.default_metapage.get_translation(lang)

        data['path_tuples'].append((path, lang, page))

    return render_to_response('nexus/ajax/node_info.html', data, 
        context_instance=RequestContext(request))

def ajax_page_info(request, page_id):
    data = _construct_page_info(request, page_id)

    return render_to_response('nexus/ajax/page_info.html', data, 
        context_instance=RequestContext(request))
