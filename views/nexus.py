# yacon.views.nexus.py
# blame ctrudeau chr(64) arsensa.com
#
# Nexus is the area for administrators to control the contents of the site,
# permissions, user management etc.  Not named the obvious "admin" to avoid conflicts
# with Django's admin features
#

from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from yacon.models.hierarchy import ContentHierarchy
from yacon.models.pages import Page

# ============================================================================
# Generic Page Display Views
# ============================================================================

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
'%s   <li><a href="%s%s/">%s</a> (<a href="/yacon/nexus/page_info/%s/">info</a>)</li>' \
                % (spacer, node.node_to_path(), page.slug, page.title, page.id))
            output.append('%s</ul>' % spacer)


def content_listing(request):
    """Renders a hierarchical list of all content pages in the system"""
    root = ContentHierarchy.get_root()
    output = ['<ul>']
    _tree_to_html_list(root, output, 0)
    output.append('</ul>')

    data = {}
    data['title'] = 'Content Listing'
    data['tree'] = "\n".join(output)

    return render_to_response('nexus/content_list.html', data, 
        context_instance=RequestContext(request))


def page_info(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    data = {}
    data['title'] = 'Page Info'
    data['page'] = page
    data['blocks'] = page.blocks.all()

    if page.is_alias():
        data['alias'] = page._alias.id

    return render_to_response('nexus/page_info.html', data, 
        context_instance=RequestContext(request))
