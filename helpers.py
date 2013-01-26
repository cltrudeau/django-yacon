# yacon.helpers.py
import logging

from django.core.exceptions import ObjectDoesNotExist

from yacon import conf
from yacon.models.site import Site
from yacon.models.pages import PageType, BlockType

logger = logging.getLogger(__name__)

# ============================================================================
# Page and Block Creation Helpers
# ============================================================================

def create_page_type(name, template, block_types=[]):
    """Creates and saves a new PageType object

    :param name: name of the PageType
    :param template: template to associate with the PageType
    :param block_types: list of BlockType objects used in the template

    :returns: the created PageType object
    """
    pt = PageType(name=name, template=template)
    pt.save()
    for block_type in block_types:
        pt.block_types.add(block_type)
    return pt


def create_dynamic_page_type(name, function_name):
    """Creates and saves a new PageType using a dynamic rendering function

    :param name: name of the PageType
    :param function_name: name of function and the module it is in to call to
        dynamically generate content for this page. Uses dot notation, example
        "module.sub.function" would do "from module.sub import function" and 
        then call "function()"

    :returns: the created PageType object
    """
    pt = PageType.objects.create(name=name, dynamic=function_name)
    return pt


def create_block_type(name, key, module_name='yacon.models.content', 
        content_handler_name='FlatContent', content_handler_parms={}):
    """Creates and saves a new BlockType object

    :param name: name of the BlockType
    :param key: identifying key of the BlockType
    :param mod: string specifying the module the ContentHandler class is in 
    :param content_handler: string specifying the name of the ContentHandler
        class for this BlockType
    :param content_handler_parms: optional dictionary of parameters to
        initialize the ContentHandler with

    :returns: the created BlockType object
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
    """Creates the base context for rendering a page, calls the custom page
    context function if defined.
    """
    site = Site.get_site(request)
    if not uri:
        uri = request.get_full_path()
    
    data = {
        'site':site,
        'request':request,
        'uri':uri,
    }

    page_context = conf.custom.page_context
    page_context(request, uri, data)

    return data


def permission_to_edit_page(request, page, context={}):
    """Calls user.permission_to_edit_page() on the user in the request, or
    returns False if no user in the request."""
    if hasattr(request, 'user') and request.user.is_authenticated():
        try:
            profile = request.user.get_profile()
            return profile.permission_to_edit_page(page, context)
        except ObjectDoesNotExist:
            return False

    return False

