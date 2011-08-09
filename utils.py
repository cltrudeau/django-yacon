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


def create_page(spec):
    """Creates a Page object by processing a dictionary that specifies how to 
    construct the page.  

    @param specifier: a dictionaries that indicates how to construct a Page.  
        The format of the dictionary is as follows:

        spec = {
            'page_type': page_type,   # the Page's PageType object
            'node': node,             # Node where the Page resides
            'language': language,     # default Language for the Page
            'translations': {         # container for translated items
                language : {          # maps Language object to translatables
                    'slug': slug,     # slug for page
                    'title': title,   # optional title for page
                    'blocks': [       # list of tuples for blocks
                        (block_type,  # BlockType object
                        content),     # content for block
                    ],
                }
            }
        }
    """
    tx = {}
    for lang, stuff in spec['translations'].items():
        if stuff.has_key('title'):
            tx[lang] = (stuff['slug'], stuff['title'])
        else:
            tx[lang] = stuff['slug']

    # create the Page
    page = Page.create_page(spec['node'], spec['page_type'], spec['language'], 
        tx)

    # create the blocks in the page
    for lang in spec['translations'].keys():
        for block_type, content in spec['translations'][lang]['blocks']:
            page.create_block(block_type, content, lang)

    return page
