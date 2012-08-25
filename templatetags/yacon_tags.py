# yacon.yacon_tags.py
# blame ctrudeau chr(64) arsensa.com
#
# Defines specialized template tags for the rendering of content from the CMS

import logging, traceback
from django import template
from django.template import loader
from django.template.base import Node

from yacon.models.pages import BlockType
from yacon.models.hierarchy import Menu

register = template.Library()
logger = logging.getLogger(__name__)

# ============================================================================
# Utility Methods
# ============================================================================

# templates for blocks
templates = {
    'editable': loader.get_template('blocks/editable.html'),
    'title_editable': loader.get_template('blocks/title_editable.html'),

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


def _valum_widget(url, node, extensions=None):
    allowed_ext = ''
    if extensions:
        allowed_ext = 'allowedExtensions: %s,' % extensions

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
""" % (url, allowed_ext, node)

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
    """Performs same actions as :func:`block_by_key` except the resulting
    content is wrapped in order to be used by the ajax editing functions.

    The template for wrapping the content is found in "blocks/editable.html"
    and is loaded using the django template loader so it can be overloaded.
    """
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
    context['page'] = page
    content = templates['title_editable'].render(context)
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

    if 'page' in context:
        language = context['page'].language
        select = context['page'].metapage
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
def upload_widget(node):
    """Returns a Valum Uploader widget wired to the general purpose uploading
    URL.

    :param node: storage type (public or private) and path indicator, e.g.
        "public:foo/bar" to have the uploaded file go in MEDIA_ROOT/foo/bar.
    """
    return _valum_widget('/yacon/nexus/uploads/upload_file/', node)


@register.simple_tag()
def user_upload_widget(node):
    """Returns a Valum Uploader widget that uploads files based on the user's
    home directory.

    :param node: storage type (public or private) and path indicator, e.g.
        "public:foo/bar" to have the uploaded file go in 
        MEDIA_ROOT/$USERNAME/foo/bar.
    """
    return _valum_widget('/yacon/nexus/uploads/user_upload_file/', node)


@register.simple_tag()
def image_upload_widget(node):
    """Returns a Valum Uploader widget that uploads images.

    :param node: storage type (public or private) and path indicator, e.g.
        "public:foo/bar" to have the uploaded file go in MEDIA_ROOT/foo/bar.
    """
    return _valum_widget('/yacon/nexus/uploads/upload_image/', node, 
        extensions="['jpg', 'jpeg', 'png', 'gif']")
