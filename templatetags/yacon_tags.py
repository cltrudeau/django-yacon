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
def menu(context, name, separator=''):
    """Returns the <li> and nested <ul> representation of the named menu.
    Note that this does not include the surround <ul> tags, this is on purpose
    so that you can add content in the templates."""
    results = []

    menu = Menu.objects.get(site=context['site'], name=name)
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
def jquery_uploader_template():
    """jQuery Template mechanism uses the same syntax as the django template
    mechanism, this tag is print out the literal jquery template.  Once Django
    1.5 is released this should be put back in a template file with the
    "verbatim" tag.
    """
    return \
"""
<!-- The template to display files available for upload -->
<script id="template-upload" type="text/x-tmpl">
{% for (var i=0, file; file=o.files[i]; i++) { %}
    <tr class="template-upload fade">
        <td class="delete"><br/></td>
        <td class="preview"><span class="fade"></span></td>
        <td class="name"><span>{%=file.name%}</span></td>
        <td class="size"><span>{%=o.formatFileSize(file.size)%}</span></td>
        {% if (file.error) { %}
            <td class="error" colspan="2"><span class="label label-important">{%=locale.fileupload.error%}</span> {%=locale.fileupload.errors[file.error] || file.error%}</td>
        {% } else if (o.files.valid && !i) { %}
            <td>
                <div class="progress progress-success progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="bar" style="width:0%;"></div></div>
            </td>
            <td class="start">{% if (!o.options.autoUpload) { %}
                <button class="btn btn-primary">
                    <i class="icon-upload icon-white"></i>
                    <span>{%=locale.fileupload.start%}</span>
                </button>
            {% } %}</td>
        {% } else { %}
            <td colspan="2"></td>
        {% } %}
        <td class="cancel">{% if (!i) { %}
            <button class="btn btn-warning">
                <i class="icon-ban-circle icon-white"></i>
                <span>{%=locale.fileupload.cancel%}</span>
            </button>
        {% } %}</td>
    </tr>
{% } %}
</script>
<!-- The template to display files available for download -->
<script id="template-download" type="text/x-tmpl">
{% for (var i=0, file; file=o.files[i]; i++) { %}
    <tr class="template-download fade">
        <td class="delete">
            <input type="checkbox" name="delete" value="1">
            <button class="btn btn-danger" data-type="{%=file.delete_type%}" data-url="{%=file.delete_url%}">
                <i class="icon-trash icon-white"></i>
            </button>
        </td>
        {% if (file.error) { %}
            <td></td>
            <td class="name"><span>{%=file.name%}</span></td>
            <td class="size"><span>{%=o.formatFileSize(file.size)%}</span></td>
            <td class="error" colspan="2"><span class="label label-important">{%=locale.fileupload.error%}</span> {%=locale.fileupload.errors[file.error] || file.error%}</td>
        {% } else { %}
            <td class="preview">
                {% if (file.thumbnail_url) { %}
                    <a href="{%=file.url%}" title="{%=file.name%}" 
                        rel="gallery">
                        <img src="{%=file.thumbnail_url%}">
                    </a>
                {% } else { %}
                    <div style="width:80px"></div>
                {% } %}
            </td>
            <td class="name">
                <a target="_blank" href="{%=file.url%}" title="{%=file.name%}" 
                    rel="{%=file.thumbnail_url&&'gallery'%}">{%=file.name%}</a>
            </td>
            <td class="size"><span>{%=o.formatFileSize(file.size)%}</span></td>
            <td colspan="2"></td>
        {% } %}
    </tr>
{% } %}
</script>
"""
