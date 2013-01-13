# yacon.yacon_tags.py
# blame ctrudeau chr(64) arsensa.com
#
# Defines specialized template tags for the rendering of content from the CMS

import logging, traceback, json

from django import template
from django.template import loader

from yacon import conf
from yacon.models.pages import BlockType
from yacon.models.hierarchy import Menu
from yacon.utils import SummarizedPage

register = template.Library()
logger = logging.getLogger(__name__)

# ============================================================================
# Utility Methods
# ============================================================================

# templates for blocks
templates = {
    'editable': loader.get_template('blocks/editable.html'),
    'title_editable': loader.get_template('blocks/title_editable.html'),
    'createable': loader.get_template('blocks/createable.html'),
    'page_last_updated': loader.get_template('blocks/page_last_updated.html'),

    # errors
    'no_such_block_type': 
        loader.get_template('blocks/errors/no_such_block_type.html'),
    'no_such_block': loader.get_template('blocks/errors/no_such_block.html'),
    'exception': loader.get_template('blocks/errors/exception.html'),
}


def _render_block_by_key(context, tag_name, key):
    """Searches for a block within a given page.  Returns a tuple of (boolean
    success, rendered tag).  Expects a tag parameter called "key" and a
    template variable called "page", which is a Page object.

    :param tag_name: name of tag being rendered
    :param key: key of block to be rendered

    :returns: (boolean, string) tuple indicating success and resulting text.
        Success may be False and still have content which would be the error
        to present to the user.
    """
    # fetch the blocks for this page
    logger.debug('key is: %s' % key)
    blocks = context['page'].blocks.filter(block_type__key=key)

    context['tag_name'] = tag_name
    context['tag_parameters'] = {
        'key':key,
    }

    if len(blocks) == 0:
        # block not found
        return (False, templates['no_such_block'].render(context))

    # grab the first block sent in
    block = blocks[0]
    try:
        context['block'] = block
        request = context['request']
        return (True, block.render(request, context))
    except Exception:
        context['exception'] = traceback.format_exc()
        return (False, templates['exception'].render(context))


def _render_menuitem(menuitem, language, selected, last, separator, indent):
    spacing = indent * '    '
    results = []
    translations = menuitem.menuitemtranslation_set.filter(language=language)

    li_class = ''
    if menuitem.metapage:
        page = menuitem.metapage.get_translation(language=language)
        if page:
            name = page.title
            if len(translations) != 0:
                name = translations[0].name

            content = '<a href="%s">%s</a>' % (page.uri, name)
        else:
            content = '<i>empty translation (%s)</i>' % language.code
            if len(translations) != 0:
                content = translations[0].name
    else:
        if len(translations) == 0:
            content = '<i>empty translation (%s)</i>' % language.code
        else:
            content = translations[0].name

    if menuitem.metapage == selected:
        li_class = ' class="selected"'

    if last:
        separator = ''

    li = '%s<li%s> %s%s</li>' % (spacing, li_class, content, separator)
    results.append(li)

    children = menuitem.get_children()
    if len(children) != 0:
        results.append('%s<ul>' % spacing)
        for child in menuitem.get_children():
            subitems = _render_menuitem(child, language, selected, last,
                separator, indent + 1)
            results.append(subitems)

        results.append('%s</ul>' % spacing)

    return '\n'.join(results)


def _valum_widget(url, node, extensions=None, on_complete=''):
    allowed_ext = ''
    if extensions:
        allowed_ext = 'allowedExtensions: %s,' % extensions

    if on_complete:
        on_complete = 'onComplete: %s,' % on_complete

    return \
"""
    <script src="/static/js/valum_uploader/fileuploader.js" ></script>

    <script type="text/JavaScript">
        $(document).ready(function(){
            var uploader = new qq.FileUploader({
                action: "%s",
                element: $('#file-uploader')[0],
                multiple: true,
                %s
                %s
                params: {
                    'node':'%s'
                }
              }) ;
        });
    </script>

    <link href="/static/js/valum_uploader/fileuploader.css" media="screen" 
        rel="stylesheet" type="text/css" />

    <div id="file-uploader">       
    </div>
""" % (url, allowed_ext, on_complete, node)

# ============================================================================
# Template Tags
# ============================================================================

@register.simple_tag(takes_context=True)
def block_by_key(context, key):
    """Searches for and renders a block whose associated BlockType object has
    a key with the given name.  The search is done on a Page object passed in
    via the context (where the page is named 'page').  If more than one block
    has the same key then an indetereminate single block is still rendered.

    Both a hardcoded string or a template variable can be used to specify the
    key.  If no block is found or there is an error rendering the block an
    error message is rendered instead.  

    Block rendering is done through the Block's BlockType's ContentHandler
    object.  The rendering method requires the request, uri, node and slugs of
    which the request, uri and slugs have to be in the context.

    Example:
    {% block_by_key "poll" %}

    The above renders the first block with the key "poll" for the associated
    page in the context.

    Example:
    {% block_by_key key %}

    The above renders the first block whose key name matches the contents of
    the template variable 'key'.  If the variable contained "poll" it would be
    equivalent to the previous example.
    """
    (success, content) = _render_block_by_key(context, 'block_by_key', key)
    return content


@register.simple_tag(takes_context=True)
def editable_block_by_key(context, key):
    """If the tag is rendering in a page being created then this renders the
    appropriate wrappers for content for the given block key.  If it is in
    display/edit more then this function performs same actions as
    :func:`block_by_key` except the resulting content is wrapped in order to
    be used by the ajax editing functions.

    The template for wrapping blocks in create mode is found in
    "blocks/createable.html", for display and edit the content is found in
    "blocks/editable.html".  Wrapper content is loaded using the django
    template loader so it can be overloaded.
    """
    create_mode = context.get('create_mode', False)
    if create_mode:
        page_type = context['page_type']
        block_type = None
        for bt in page_type.block_types.all():
            if bt.key == key:
                block_type = bt
                break

        if not block_type:
            return templates['no_such_block_type'].render(context)

        context['key'] = key
        context['block_type_id'] = block_type.id
        content = templates['createable'].render(context)
    else:
        (success, content) = _render_block_by_key(context, 'block_by_key', key)
        if success:
            # didn't get an error, wrap the content using the editable template 
            context['content'] = content
            content = templates['editable'].render(context)

    return content


@register.simple_tag(takes_context=True)
def editable_page_title(context, page):
    """Prints the title of the page for the given page, wrapping the 
    title in a widget that allows editing via ajax.  
    
    The template for wrapping the content is found in 
    "blocks/title_editable.html" and is loaded using the django template 
    loader so it can be overloaded.
    """
    create_mode = context.get('create_mode', False)
    if create_mode:
        # don't show this tag when in create mode, handled by create form
        return ''

    context['page'] = page
    content = templates['title_editable'].render(context)
    return content


@register.simple_tag(takes_context=True)
def page_last_updated(context, page):
    """Returns the most recent timestamp of the given page or all of its
    blocks.  Content is wrapped in a template with divs that yacon/editable.js
    is aware of to change the value via ajax when something on the page is
    edited.
    
    The template for wrapping the content is found in 
    "blocks/page_last_updated.html" and is loaded using the django template 
    loader so it can be overloaded.
    """
    context['page'] = page
    content = templates['page_last_updated'].render(context)
    return content


@register.simple_tag(takes_context=True)
def menu(context, name, separator=''):
    """Returns the <li> and nested <ul> representation of the named menu.
    Note that this does not include the surround <ul> tags, this is on purpose
    so that you can add content in the templates."""
    results = []

    try:
        menu = Menu.objects.get(site=context['site'], name=name)
    except Menu.DoesNotExist:
        logger.error('no menu matching name "%s"', name)
        return ''

    page = context.get('page', None)
    if page:
        language = page.language
        select = page.metapage
    else:
        language = context['site'].default_language
        select = None

    items = list(menu.first_level.all())
    for item in items:
        last = (item == items[-1])
        menuitem = _render_menuitem(item, language, select, last, separator, 1)
        results.append(menuitem)

    return '\n'.join(results)


@register.simple_tag(takes_context=True)
def dynamic_content_by_key(context, key):
    """DynamicContent content handlers do not require any Block to be stored
    in the database, but can be fired directly.  A BlockType is registered
    as usual, but this method, unlike block_by_key, doesn't look for a Block,
    but renders the ContentHandler directly."""
    # fetch the named block type
    logger.debug('key is: %s' % key)
    context['tag_name'] = 'dynamic_content_by_key'
    context['tag_parameters'] = {
        'key':key,
    }
    try:
        block_type = BlockType.objects.get(key=key)
        request = context['request']
        handler = block_type.get_content_handler()
        return handler.render(request, context, None)
    except BlockType.DoesNotExist:
        return templates['no_such_block_type'].render(context)
    except Exception:
        context['exception'] = traceback.format_exc()
        return templates['exception'].render(context)


@register.simple_tag(takes_context=True)
def tsort(context, name):
    """Used to produce the ascending/descending links for sorting a table.

    :param name: name of the tag to print the tsort for, if the request object
        contains a "sort" parameter that matches this name then the links will
        show selection appropriately

    :returns: html containing links and images for sorting a table
    """
    request = context['request']
    sort = request.GET.get('sort')
    if not sort:
        sort = context.get('default_sort')
    direction = request.GET.get('direction')

    request.path

    lines = [
        '<a href="%s?sort=%s">' % (request.path, name), 
        '<img ',
    ]
    if sort == name and direction != 'rev':
        lines.append('class="selected" ')

    lines.extend([
        'src="/static/icons/fatcow/sort_down.png">',
        '</a>',
        '<a href="%s?sort=%s&direction=rev">' % (request.path, name),
        '<img '
    ])

    if sort == name and direction == 'rev':
        lines.append('class="selected" ')

    lines.extend([
        'src="/static/icons/fatcow/sort_up.png">',
        '</a>',
    ])

    return ''.join(lines)


@register.simple_tag()
def upload_widget(node, on_complete=''):
    """Returns a Valum Uploader widget wired to the general purpose uploading
    URL.

    :param node: storage type (public or private) and path indicator, e.g.
        "public:foo/bar" to have the uploaded file go in MEDIA_ROOT/foo/bar.
    :param on_complete: name of Javascript function to call when an upload has
        complete, will be called with signature:
        function(String id, String fileName, Object responseJSON)
    """
    return _valum_widget('/yacon/browser/upload_file/', node,
        on_complete=on_complete)


@register.simple_tag()
def user_upload_widget(node, on_complete=''):
    """Returns a Valum Uploader widget that uploads files based on the user's
    home directory.

    :param node: storage type (public or private) and path indicator, e.g.
        "public:foo/bar" to have the uploaded file go in 
        MEDIA_ROOT/$USERNAME/foo/bar.
    :param on_complete: name of Javascript function to call when an upload has
        complete, will be called with signature:
        function(String id, String fileName, Object responseJSON)
    """
    return _valum_widget('/yacon/browser/user_upload_file/', node,
        on_complete=on_complete)


@register.simple_tag()
def image_upload_widget(node, on_complete=''):
    """Returns a Valum Uploader widget that uploads images.

    :param node: storage type (public or private) and path indicator, e.g.
        "public:foo/bar" to have the uploaded file go in MEDIA_ROOT/foo/bar.
    :param on_complete: name of Javascript function to call when an upload has
        complete, will be called with signature:
        function(String id, String fileName, Object responseJSON)
    """
    extensions = json.dumps(conf.site.image_extensions)

    return _valum_widget('/yacon/browser/upload_file/', node, 
        extensions=extensions, on_complete=on_complete)


@register.simple_tag()
def user_image_upload_widget(node, on_complete=''):
    """Returns a Valum Uploader widget that uploads images based on the user's
    home directory.

    :param node: storage type (public or private) and path indicator, e.g.
        "public:foo/bar" to have the uploaded file go in MEDIA_ROOT/foo/bar.
    :param on_complete: name of Javascript function to call when an upload has
        complete, will be called with signature:
        function(String id, String fileName, Object responseJSON)
    """
    extensions = json.dumps(conf.site.image_extensions)

    return _valum_widget('/yacon/browser/user_upload_file/', node, 
        extensions=extensions, on_complete=on_complete)


@register.simple_tag(takes_context=True)
def regroup(context, listing, size):
    """Takes a list and creates a new list of lists that are "size" long and
    puts it in a variable named "grouped".  This is done in a tag so that it
    can be done after pagination for performance reasons."""

    grouped = []
    subgroup = []
    count = 0
    for item in listing:
        if count == size:
            grouped.append(subgroup)
            subgroup = []
            count = 0

        subgroup.append(item)
        count += 1

    if subgroup:
        grouped.append(subgroup)

    context['grouped'] = grouped
    return ''


@register.simple_tag(takes_context=True)
def summarize_pages(context, pages, block_key, summary_size):
    """Takes a list of Page objects and creates a list of SummarizePage
    objects.  This is done in a tag as it should be done after pagination for
    performance reasons.  Puts a variable in the context called "summaries".

    :param pages: list of pages to convert
    :param block_key: name of block key used to produce summary text
    :param summary_size: number of characters to include in the summary block

    :returns: nothing, inserts a "summaries" list in the context
    """
    summaries = []
    for page in pages:
        summaries.append(SummarizedPage(page, block_key, summary_size))

    context['summaries'] = summaries

    return ''


@register.simple_tag(takes_context=True)
def summarize_pages_from_highlighted_blocks(context, blocks, summary_size):
    """Takes a list of Block objects that have been returned from a
    highlighted search and creates the corresponding SummarizePage objects.
    This is done in a tag as it should be done after pagination.  Puts a
    variable in the context called "summaries".

    :param blocks: list of blocks to get pages from
    :param summary_size: number of characters to include in the summary block

    :returns: nothing, inserts a "summaries" list in the context
    """
    summaries = SummarizedPage.factory_from_highlighted_blocks(blocks, 
        summary_size)

    context['summaries'] = summaries
    return ''
