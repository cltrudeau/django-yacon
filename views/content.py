# yacon.views.user.py
# blame ctrudeau chr(64) arsensa.com

import logging, urllib

from django.contrib.auth.decorators import login_required
from django.forms.util import ErrorList
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import formats

from django.views.decorators.csrf import csrf_exempt

from yacon.decorators import post_required
from yacon.forms import CreatePageForm
from yacon.helpers import prepare_context, has_edit_permissions
from yacon.models.site import Site
from yacon.models.hierarchy import BadSlug
from yacon.models.pages import Block, Page, PageType, Translation, MetaPage
from yacon.models.files import StoredFile, FileSpec
from yacon.utils import JSONResponse

logger = logging.getLogger(__name__)

# ============================================================================
# Constants

PAGE_CONTEXT = None

# ============================================================================
# Generic Page Display Views
# ============================================================================

def display_page(request, uri=''):
    """Default page rendering method for the CMS.  Uses the request object to
    determine what site is being displayed and the uri passed in to find an
    page to render. """
    data = prepare_context(request, uri)
    page = data['site'].find_page(uri)
    
    if page == None:
        # no such page found for uri
        raise Http404('CMS did not contain a page for uri: %s' % uri)

    data.update({
        'page':page,
        'create_mode':False,
        'translations':page.other_translations(),
        'edit_permission':has_edit_permissions(request, page),
    })

    return page.metapage.page_type.render(request, data)


@login_required
def create_page(request, page_type_id, language_code, auto_slug, uri):
    data = prepare_context(request, uri)
    site = data['site']
    auto_slug = bool(auto_slug)
    page_type = get_object_or_404(PageType, id=page_type_id)
    langs = site.get_languages(language_code)
    if len(langs) == 0:
        lang = site.default_language
    else:
        lang = langs[0]

    try:
        profile = request.user.get_profile()
    except:
        raise Http404('user had no profile')

    parsed_path = site.parse_path(uri)
    node = parsed_path.node
    if not parsed_path.node:
        raise Http404('uri "%s" did not lead to valid node' % uri)

    if not profile.permission_to_create_page(page_type, node):
        raise Http404('permission to create was denied')

    if request.method == 'POST':
        form = CreatePageForm(request.POST)
        if form.is_valid():
            clean = form.cleaned_data
            title = clean.pop('title', '')
            slug = clean.pop('slug', '')
            auto_slug = clean.pop('auto_slug', '')
            if auto_slug:
                slug = title

            block_types = {}
            for block_type in page_type.block_types.all():
                block_types[block_type.key] = block_type

            block_hash = {}
            for key, value in clean.items():
                block_type = block_types.get(key, None)
                if not block_type:
                    raise Http404(('block type key "%s" ' % key +\
                        'not registered with PageType %s' % page_type))

                block_hash[block_type] = urllib.unquote_plus(value)

            # create the MetaPage and Page, then redirect to the page just 
            # created
            try:
                metapage = MetaPage.create_page(node, page_type, title, slug,
                    block_hash, owner=request.user, auto_slug=auto_slug)
                page = metapage.get_translation(lang)
                return HttpResponseRedirect(page.uri)
            except BadSlug:
                errors = form._errors.setdefault('slug', ErrorList())
                errors.append(('Slug did not validate, either malformed or '
                    'duplicate'))
    else: # GET
        form = CreatePageForm(initial={'auto_slug':auto_slug})

    data.update({
        'create_mode':True,
        'page_type':page_type,
        'create_form':form,
        'edit_permission':True,
        'page':None,
    })

    return page_type.render(request, data)

# ============================================================================
# Ajax Views
# ============================================================================

@login_required
@post_required
def replace_block(request):
    """Ajax view for submitting edits to a block."""
    if not request.REQUEST.has_key('block_id'):
        raise Http404('replace_block requires "block_id" parameter')

    if not request.REQUEST.has_key('content'):
        raise Http404('replace_block requires "content" parameter')

    try:
        # block parameter is 'block_X' where X is the id we're after
        block_id = request.POST['block_id'][6:]
        block = Block.objects.get(id=block_id)
    except Block.DoesNotExist:
        raise Http404('no block with id "%s"' % block_id)

    # check permissions
    if not request.user.is_superuser:
        # one of the pages associated with the block must belong to the user
        # logged in 
        pages = block.page_set.filter(owner=request.user)
        if len(pages) == 0:
            raise Http404('permission denied')

    # set the new block content
    block.content = urllib.unquote(request.POST['content'])
    block.save()

    last_updated_list = []
    for page in block.page_set.all():
        when = formats.date_format(page.last_updated, 'DATETIME_FORMAT')
        last_updated_list.append((page.id, when))
    result = {
        'success':True,
        'block_id':block.id,
        'last_updated_list':last_updated_list,
    }
    print '*** result: ', result
    response = JSONResponse(result, extra_headers={'Cache-Control':'no-cache'})
    print '*** response: ', response
    return response


@login_required
@post_required
def replace_title(request):
    """Ajax view for submitting edits to a block."""
    if not request.REQUEST.has_key('page_id'):
        raise Http404('replace_title requires "page_id" parameter')

    if not request.REQUEST.has_key('content'):
        raise Http404('replace_title requires "content" parameter')

    try:
        # page parameter is 'page_X' where X is the id we're after
        page_id = request.POST['page_id'][5:]
        page = Page.objects.get(id=page_id)
    except Page.DoesNotExist:
        raise Http404('no page with id "%s"' % page_id)

    # check permissions
    if not request.user.is_superuser:
        # page must belong to logged in user
        if page.owner != request.user:
            raise Http404('permission denied')

    # set the new block content
    page.title = urllib.unquote(request.POST['content'])
    page.save()

    result = {
        'success':True,
        'last_updated':formats.date_format(page.last_updated, 
            'DATETIME_FORMAT'),
        'page_id':page.id,
    }
    response = JSONResponse(result, extra_headers={'Cache-Control':'no-cache'})
    return response
