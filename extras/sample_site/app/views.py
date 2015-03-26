# app.views.py
#
# Views for dynamic content
import logging, urllib

from django.template import RequestContext
from django.shortcuts import render_to_response

from yacon.models.pages import Page, PageType, Block
from yacon.utils import QuerySetChain

logger = logging.getLogger(__name__)

# ============================================================================

NEWS_PAGE_TYPE = None

# ============================================================================
# Dynamic Views
# ============================================================================

def news_listing(request, data):
    global NEWS_PAGE_TYPE

    search = request.GET.get('q')
    if search:
        search = urllib.unquote(search)
        blocks = Block.search(search, block_key='news', highlighted=True)
        data.update({
            'search':True,
            'search_terms':search,
            'blocks':blocks,
        })
    else:
        # find all of the blogs in the system and list them
        if not NEWS_PAGE_TYPE:
            NEWS_PAGE_TYPE = PageType.objects.get(name='News Type')

        # return all possible news items
        news_items = Page.find_by_page_type(NEWS_PAGE_TYPE).order_by('-created')

        # return enitre listing, summarization will be done by template tag on
        # the page
        data.update({
            'news_items':news_items,
        })
    return render_to_response('news_listing.html', data, 
        context_instance=RequestContext(request))
