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
from yacon.models.pages import Page, PageTranslation

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
        pages = Page.objects.filter(node=node)
        if len(pages) != 0:
            output.append('%s<ul class="content_list">' % spacer)
            for page in pages:
                pt = page.get_default_translation()

                # output the list item for the primary language
                output.append(spacer + '   <li>' +\
                    '<img src="/static/icons/fatcow/page.png">&nbsp;' +\
                    '<a class="obj_info" ' + \
                    'href="/yacon/nexus/ajax_pagetranslation_info/%d/">%s</a>' \
                    % (pt.id, pt.title))

                for tx in pt.other_translations():
                    output.append('(<a class="obj_info" href="' +\
                        '/yacon/nexus/ajax_pagetranslation_info/%d/">%s</a>)' \
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


def _construct_pagetranslation_info(request, translation_id):
    pt = get_object_or_404(PageTranslation, id=translation_id)
    data = {}
    data['title'] = 'Page Info'
    data['pagetranslation'] = pt
    data['blocks'] = pt.blocks.all()
    data['uri'] = pt.get_uri()

    #if page.is_alias():
    #    data['alias'] = page._alias.id

    return data

def pagetranslation_info(request, page_id):
    data = _construct_pagetranslation_info(request, page_id)

    return render_to_response('nexus/pagetranslation_info.html', data, 
        context_instance=RequestContext(request))

# ============================================================================
# Ajax Methods
# ============================================================================

def ajax_node_info(request, node_id):
    node = Node.objects.get(id=node_id)
    if node == None:
        return HttpResponse('')

    data = {}
    data['path'] = node.node_to_path()
    data['default_page'] = node.default_page
    if node.default_page != None:
        data['default_page_uri'] = node.default_page.get_uri()

    data['num_pages'] = len(Page.objects.filter(node=node))
    data['path_aliases'] = []

    langs = node.site.get_languages()
    default = node.site.default_language
    for lang in langs:
        if lang == default:
            continue

        data['path_aliases'].append((lang, node.node_to_path(lang)))

    return render_to_response('nexus/ajax/node_info.html', data, 
        context_instance=RequestContext(request))

def ajax_pagetranslation_info(request, page_id):
    data = _construct_pagetranslation_info(request, page_id)

    return render_to_response('nexus/ajax/pagetranslation_info.html', data, 
        context_instance=RequestContext(request))
