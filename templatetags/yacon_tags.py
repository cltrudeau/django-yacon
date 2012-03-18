# yacon.yacon_tags.py
# blame ctrudeau chr(64) arsensa.com
#
# Defines specialized template tags for the rendering of content from the CMS

import logging, traceback
from django import template
from django.template import loader

register = template.Library()
logger = logging.getLogger(__name__)

# ============================================================================
# Utility Methods
# ============================================================================

# templates for blocks
templates = {
    'editable': loader.get_template('blocks/editable.html'),

    # errors
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
        return (True, block.render(request))
    except Exception, e:
        context['exception'] = traceback.format_exc()
        return (False, templates['exception'].render(context))

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
