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

def _tree_to_html_list(node, output, indent):
    spacer = 3 * (indent + 1) * ' '
    name = '%s (%s)' % (node.name, node.slug)
    if node.name == None:
        name = '<i>empty translation (%s)</i>' %\
            node.site.default_language.identifier

    output.append(('%s<li>' % spacer + 
        '<img src="/static/icons/fatcow/folder.png">&nbsp;'
        '<a class="node_link folder" href="/yacon/nexus/ajax_node_info'
        '/%d/">%s<a/>' % (node.id, name) + '</li>'))
    
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
                image = "/static/icons/fatcow/page_white.png"
                if metapage.is_alias():
                    image = "/static/icons/fatcow/page_white_link.png"
                page = metapage.get_default_translation()
                if page == None:
                    title = '<i>empty translation (%s)</i>' % \
                        node.site.default_language.identifier
                else:
                    title = page.title
                output.append(('%s   <li><img src="%s">' % (spacer, image) +
                    '&nbsp;<a class="node_link metapage" ' 
                    'href="/yacon/nexus/ajax_metapage_info/%s/">' \
                    % metapage.id + '%s</a></li>' % title))

            output.append('%s</ul>' % spacer)

# ============================================================================
# Ajax Methods
# ============================================================================

def ajax_node_info(request, node_id):
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


def ajax_metapage_info(request, metapage_id):
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


def ajax_get_sites(request):
    sites = Site.objects.all()
    data = {}
    for site in sites:
        data[site.id] = site.name

    return HttpResponse(json.dumps(data), content_type='application/json')


def ajax_site_info(request, site_id):
    site = get_object_or_404(Site, id=site_id)
    url = SiteURL.objects.get(site=site)

    data = {
        'site':site,
        'url':url.base_url,
        'alternate_languages':site.alternate_language.all(),
    }
    return render_to_response('nexus/ajax/site_info.html', data,
        context_instance=RequestContext(request))


def ajax_site_tree(request, site_id):
    site = get_object_or_404(Site, id=site_id)

    output = [('<a class="node_link site" href="'
            '/yacon/nexus/ajax_site_info/%s/">Info for: %s</a>' % (site.id, 
            site.name)),
        '<br/>',
        '<ul class="node_tree">', 
    ]
    _tree_to_html_list(site.doc_root, output, 0)
    output.append('</ul>')

    return HttpResponse('\n'.join(output))
