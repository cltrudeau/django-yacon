# app.dynamic.py
#
# Dynamic content block rendering methods

import logging

from yacon.models.pages import Page, PageType
from yacon.utils import SummarizedPage

logger = logging.getLogger(__name__)

# ============================================================================

NEWS_PAGE_TYPE = None

# ============================================================================

def page_context(request, uri, context):
    """Called by yacon.view.display_page, gives us a chance to add context to
    every page displayed."""
    global NEWS_PAGE_TYPE

    menu_name = 'Menu'

    # find the latest news
    if not NEWS_PAGE_TYPE:
        NEWS_PAGE_TYPE = PageType.objects.get(name='News Type')

    pages = Page.find_by_page_type(NEWS_PAGE_TYPE).order_by('-created')
    news = []
    for page in pages[:3]:
        item = SummarizedPage(page, 'news', 80)
        news.append(item)

    context.update({
        'menu_name': menu_name,
        'news':news,
        'advertisement':'/static/images/sample_ad.png',
    })
