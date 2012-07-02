# yacon.utils.py
# blame ctrudeau chr(64) arsensa.com

import urllib, logging

from django.conf import settings

from yacon.models.site import Site
from yacon.models.pages import PageType, BlockType

logger = logging.getLogger(__name__)

# ============================================================================
# Constants

PAGE_CONTEXT = None

# ============================================================================
# Page and Block Creation Helpers
# ============================================================================

def create_page_type(name, template):
    """Creates and saves a new PageType object

    @param name -- name of the PageType
    @param template -- template to associate with the PageType

    @returns -- the created PageType object
    """
    pt = PageType(name=name, template=template)
    pt.save()
    return pt


def create_block_type(name, key, module_name, content_handler_name,
        content_handler_parms={}):
    """Creates and saves a new BlockType object

    @param name -- name of the BlockType
    @param key -- identifying key of the BlockType
    @param mod -- string specifying the module the ContentHandler class is
        found in 
    @param content_handler -- string specifying the name of the ContentHandler
        class for this BlockType
    @param content_handler_parms -- optional dictionary of parameters to
        initialize the ContentHandler with

    @returns -- the created BlockType object
    """
    bt = BlockType(name=name, key=key, module_name=module_name, 
        content_handler_name=content_handler_name, 
        content_handler_parms=content_handler_parms)
    bt.save()
    return bt

# ============================================================================
# View Helpers
# ============================================================================

def prepare_context(request, uri=None):
    """Creates the base context for rendering a page.  Includes calling the 
    settings.YACON_PAGE_CONTEXT method if defined.
    """
    site = Site.get_site(request)
    if not uri:
        uri = request.get_full_path()
    
    data = {
        'site':site,
        'request':request,
        'uri':uri,
    }

    if settings.YACON_PAGE_CONTEXT:
        global PAGE_CONTEXT
        if not PAGE_CONTEXT:
            fn_name = None
            mod_name = None
            try:
                logger.debug('about to import %s' % settings.YACON_PAGE_CONTEXT)

                parts = settings.YACON_PAGE_CONTEXT.split('.')
                fn_name = parts[-1]
                mod_name = '.'.join(parts[:-1])

                mod = __import__(mod_name, globals(), locals(), [fn_name])
                logger.debug('mod import successful')

                PAGE_CONTEXT = getattr(mod, fn_name)
            except Exception, e:
                msg = ('importing YACON_PAGE_CONTEXT caused exception, setting:'
                    '"%s", module name:"%s", function name: "%s"' % (
                    settings.YACON_PAGE_CONTEXT, mod_name, fn_name))
                logger.exception(msg)
                raise e

        PAGE_CONTEXT(request, uri, data)

    return data
