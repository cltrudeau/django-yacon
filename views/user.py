# yacon.views.user.py
# blame ctrudeau chr(64) arsensa.com

import urllib, logging
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404

from yacon.models.hierarchy import ContentHierarchy
from yacon.models.pages import Page

# ============================================================================
# Generic Page Display Views
# ============================================================================

def display_page(request, uri):
    """Renders a page corresponding to the uri passed in.  Uses the uri to
    look up a node in the ContentHierarchy and finds a corresponding page.  A
    dictionary of the content blocks is created and passed to the template for
    the page."""
    parsed = ContentHierarchy.parse_path('/' + uri)
    if parsed.node == None:
        # weren't able to parse the path
        raise Http404('Path not found.  Parsed: path=%s' % parsed.path)

    # find the page that corresponds to the uri
    try:
        page = Page.objects.get(node=parsed.node, 
            slug=parsed.slugs_after_node[0])
    except Page.DoesNotExist:
        raise Http404('Page not found for: node=%s, slug=%s' % \
            (parsed.node, parsed.slugs_after_node[0]))

    logging.debug('displaying page: %s' % page)
    data = {}
    data['page'] = page
    data['blocks'] = page.content_dict(request, uri, parsed.slugs_after_node)

    return render_to_response(page.pagetype.template, data, 
        context_instance=RequestContext(request))


def _tree_to_html_list(node, output, indent):
    spacer = 3 * (indent + 1) * ' '
    output.append('%s   <li>%s (%s)</li>' % (3*indent*' ', node.name, 
        node.slug))
    if node.has_children():
        output.append('%s<ul>' % spacer)
        for child in node.get_children():
            _tree_to_html_list(child, output, indent+1)
        output.append('%s</ul>' % spacer)
    else: 
        # leaf node, check for pages
        pages = Page.objects.filter(node=node)
        if len(pages) != 0:
            output.append('%s<ul>' % spacer)
            for page in pages:
                output.append(\
'%s   <li><a href="%s%s/">%s</a> (<a href="/yacon/admin/page_info/%s/">?</a>)</li>' % (\
                    spacer, node.node_to_path(), page.slug, page.title))
            output.append('%s</ul>' % spacer)


def content_listing(request):
    """Renders a hierarchical list of all content pages in the system"""
    root = ContentHierarchy.get_root()
    output = ['<ul>']
    _tree_to_html_list(root, output, 0)
    output.append('</ul>')

    data = {}
    data['tree'] = "\n".join(output)

    return render_to_response('admin/content_list.html', data, 
        context_instance=RequestContext(request))


def page_info(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    data = {}
    data['page'] = page
    data['blocks'] = page.content_dict(request, 'fake uri', ['fake slug'])

    return render_to_response('admin/page_info.html', data, 
        context_instance=RequestContext(request))


# ============================================================================
# Submittal Views
# ============================================================================

def ajax_submit(request):
    """Used for submitting user generated content to the system"""

    if request.method != 'POST':
        raise Http404('GET method not supported for ajax_submit')

    if not request.REQUEST.has_key('block_id'):
        raise Http404('ajax_submit requires "block_id" parameter')

    # ok, we've got the page, now get the block name
    try:
        block = Block.objects.get(pk=request.POST['block_id'])
    except:
        raise Http404( 'no block with id "%s"' % request.POST['block'])

    # set the new block content
    block.content = urllib.unquote(request.POST['content'])
    block.save()

    response = render_to_response('block_response.html', data, 
        context_instance=RequestContext(request))
    response['Cache-Control'] = 'no-cache'
    return response
