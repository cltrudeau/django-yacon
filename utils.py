# yacon.utils.py
# blame ctrudeau chr(64) arsensa.com

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


def create_block_type(name, key, module_name, content_handler_name):
    """Creates and saves a new BlockType object

    @param name -- name of the BlockType
    @param key -- identifying key of the BlockType
    @param mod -- string specifying the module the ContentHandler class is
        found in 
    @param content_handler -- string specifying the name of the ContentHandler
        class for this BlockType

    @returns -- the created BlockType object
    """
    bt = BlockType(name=name, key=key, module_name=module_name, 
        content_handler_name=content_handler_name)
    bt.save()
    return bt
