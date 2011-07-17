# yacon.utils.py
# blame ctrudeau chr(64) arsensa.com

from yacon.models.pages import PageType, Page, BlockType, Block

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


def create_page(title, slug, node, page_type, content_list):
    """Takes a list of tuples of (content, BlockType objects), creates the
    corresponding Block objects, saves them, and creates a new Page that
    contains these objects.

    @param title -- title for the page
    @param slug -- slug that identifies the page uniquely within the node
    @param node -- a hierarchy node where this page is found
    @param page_type -- a PageType instance to be associated with
    @param content_list -- a list of tuples of content and associated
        BlockType objects.  E.g. [("<i>stuff</i>", blurb_type),]

    @returns -- the new Page object
    """
    page = Page(title=title, slug=slug, node=node, page_type=page_type)
    page.save()
    for (content, block_type) in content_list:
        block = Block(block_type=block_type, content=content)
        block.save()
        page.blocks.add(block)

    return page
