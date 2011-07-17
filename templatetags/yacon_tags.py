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

# templates for errors
templates = {
    'no_such_block': loader.get_template('block_errors/no_such_block.html'),
    'exception': loader.get_template('block_errors/exception.html')
}


def _render_block(context, page, blocks, tag_name, tag_parameters):
    """Returns a string which is the generated by rendering the block or an
    error template associated with something going wrong with rendering the
    block"""

    request = context['request']
    uri = context['uri']
    slugs = context['slugs']
    context['tag_name'] = tag_name
    context['tag_parameters'] = tag_parameters

    if len(blocks) == 0:
        # block not found
        return templates['no_such_block'].render(context)

    # grab the first block sent in
    block = blocks[0]
    try:
        handler = block.block_type.get_content_handler()
        return handler.render(request, uri, page.node, slugs, block)
    except Exception, e:
        context['exception'] = traceback.format_exc()
        return templates['exception'].render(context)

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
    logger.debug('key is: %s' % key)

    page = context['page']
    blocks = page.get_blocks_by_key(key)

    return _render_block(context, page, blocks, 'block_by_key', 'key:%s' % key)
