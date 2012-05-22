# yacon.utils.py
# blame ctrudeau chr(64) arsensa.com

import urllib

from yacon.models.pages import PageType, BlockType

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
