try:
    set
except NameError:
    from sets import Set as set

from math import log10

from django import template
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage
from django.conf import settings

register = template.Library()

DEFAULT_PAGINATION = getattr(settings, 'PAGINATION_DEFAULT_PAGINATION', 20)
DEFAULT_WINDOW = getattr(settings, 'PAGINATION_DEFAULT_WINDOW', 4)
DEFAULT_ORPHANS = getattr(settings, 'PAGINATION_DEFAULT_ORPHANS', 0)
INVALID_PAGE_RAISES_404 = getattr(settings,
    'PAGINATION_INVALID_PAGE_RAISES_404', False)
MAX_CHARACTERS = getattr(settings, 'PAGINATION_MAX_CHARACTERS', 25)


def replace_context_value(context, key, value):
    # searches through all dictionaries in the context and replaces keys at
    # any level with the given value
    for d in context.dicts:
        if key in d:
            d[key] = value


def do_autopaginate(parser, token):
    """
    Splits the arguments to the autopaginate tag and formats them correctly.
    """
    split = token.split_contents()
    as_index = None
    context_var = None
    for i, bit in enumerate(split):
        if bit == 'as':
            as_index = i
            break
    if as_index is not None:
        try:
            context_var = split[as_index + 1]
        except IndexError:
            raise template.TemplateSyntaxError("Context variable assignment " +
                "must take the form of {%% %r object.example_set.all ... as " +
                "context_var_name %%}" % split[0])
        del split[as_index:as_index + 2]
    if len(split) == 2:
        return AutoPaginateNode(split[1])
    elif len(split) == 3:
        return AutoPaginateNode(split[1], paginate_by=split[2], 
            context_var=context_var)
    elif len(split) == 4:
        try:
            orphans = int(split[3])
        except ValueError:
            raise template.TemplateSyntaxError(u'Got %s, but expected integer.'
                % split[3])
        return AutoPaginateNode(split[1], paginate_by=split[2], orphans=orphans,
            context_var=context_var)
    else:
        raise template.TemplateSyntaxError('%r tag takes one required ' +
            'argument and one optional argument' % split[0])

class AutoPaginateNode(template.Node):
    """
    Emits the required objects to allow for Digg-style pagination.
    
    First, it looks in the current context for the variable specified, and using
    that object, it emits a simple ``Paginator`` and the current page object 
    into the context names ``paginator`` and ``page_obj``, respectively.
    
    It will then replace the variable specified with only the objects for the
    current page.
    
    .. note::
        
        It is recommended to use *{% paginate %}* after using the autopaginate
        tag.  If you choose not to use *{% paginate %}*, make sure to display the
        list of available pages, or else the application may seem to be buggy.
    """
    def __init__(self, queryset_var, paginate_by=DEFAULT_PAGINATION,
        orphans=DEFAULT_ORPHANS, context_var=None):
        self.queryset_var = template.Variable(queryset_var)
        if isinstance(paginate_by, int):
            self.paginate_by = paginate_by
        else:
            self.paginate_by = template.Variable(paginate_by)
        self.orphans = orphans
        self.context_var = context_var

    def render(self, context):
        key = self.queryset_var.var
        value = self.queryset_var.resolve(context)
        if isinstance(self.paginate_by, int):
            paginate_by = self.paginate_by
        else:
            paginate_by = self.paginate_by.resolve(context)
        paginator = Paginator(value, paginate_by, self.orphans)
        try:
            page_obj = paginator.page(context['request'].page)
        except InvalidPage:
            if INVALID_PAGE_RAISES_404:
                raise Http404('Invalid page requested.  If DEBUG were set to ' +
                    'False, an HTTP 404 page would have been shown instead.')
            context.dicts[0][key] = []
            context.dicts[0]['invalid_page'] = True
            return u''
        if self.context_var is not None:
            replace_context_value(context, self.context_var, 
                page_obj.object_list)
        else:
            replace_context_value(context, key, page_obj.object_list)

        # put the pagination objects into the first context dictionary so they
        # can be used across template blocks
        context.dicts[0]['paginator'] = paginator
        context.dicts[0]['page_obj'] = page_obj
        return u''


def _num_digits(value):
    return int(log10(value)) + 1


def paginate(context, window=DEFAULT_WINDOW, hashtag=''):
    """
    Renders the ``pagination/pagination.html`` template, resulting in a
    Digg-like display of the available pages, given the current page.  If there
    are too many pages to be displayed before and after the current page, then
    elipses will be used to indicate the undisplayed gap between page numbers.
    
    Requires one argument, ``context``, which should be a dictionary-like data
    structure and must contain the following keys:
    
    ``paginator``
        A ``Paginator`` or ``QuerySetPaginator`` object.
    
    ``page_obj``
        This should be the result of calling the page method on the 
        aforementioned ``Paginator`` or ``QuerySetPaginator`` object, given
        the current page.
    
    This same ``context`` dictionary-like data structure may also include:
    
    ``getvars``
        A dictionary of all of the **GET** parameters in the current request.
        This is useful to maintain certain types of state, even when requesting
        a different page.
        """
    try:
        paginator = context['paginator']
        page_obj = context['page_obj']
        page_range = paginator.page_range
        # Calculate the record range in the current page for display.
        records = {'first': 1 + (page_obj.number - 1) * paginator.per_page}
        records['last'] = records['first'] + paginator.per_page - 1
        if records['last'] + paginator.orphans >= paginator.count:
            records['last'] = paginator.count

        last_page = page_range[-1]
        digits_last = _num_digits(last_page)
        pages = [page_obj.number]
        difference = 1
        total_digits = _num_digits(page_obj.number)
        #import pudb; pudb.set_trace()
        while(True):
            # figure out how much extra we're adding due to elipses on the
            # left and right sides
            extra = 0
            if pages[0] != 1 and pages[0] != 2:
                extra = 4
            if pages[-1] != last_page and pages[-1] != last_page - 1:
                extra += 4

            # calculate space for dividers, there is a divider between each
            # item in the list but not at the ends
            dividers = len(pages) - 2
            if dividers < 0:
                dividers = 0

            extra += dividers

            if total_digits + extra + digits_last > MAX_CHARACTERS:
                # used up all our characters, add start and end parts and then
                # leave
                if pages[0] != 1:
                    # insert marker for elipses and the number one
                    if pages[0] != 2:
                        pages.insert(0, None)
                    pages.insert(0, 1)

                if pages[-1] != last_page:
                    # last number in our list isn't the last item, add elipses
                    # and the last item
                    if pages[-1] != last_page - 1:
                        pages.append(None)
                    pages.append(last_page)

                break

            # add something to the left and right (maybe)
            left = page_obj.number - difference
            if left > 0:
                pages.insert(0, left)
                total_digits += _num_digits(left)

            right = page_obj.number + difference
            if right <= last_page:
                pages.append(right)
                total_digits += _num_digits(right)

            difference += 1

            if len(pages) == last_page:
                break

        class PageHolder(object):
            pass

        before = None
        holders = []
        for page in pages:
            holder = PageHolder()
            holder.page = page
            holder.before_elipses = False
            holders.append(holder)

            if not page and before:
                before.before_elipses = True

            before = holder

        to_return = {
            'MEDIA_URL': settings.MEDIA_URL,
            'pages': pages,
            'pageholders':holders,
            'records': records,
            'page_obj': page_obj,
            'paginator': paginator,
            'hashtag': hashtag,
            'is_paginated': paginator.count > paginator.per_page,
        }
        if 'request' in context:
            getvars = context['request'].GET.copy()
            if 'page' in getvars:
                del getvars['page']
            if len(getvars.keys()) > 0:
                to_return['getvars'] = "&%s" % getvars.urlencode()
            else:
                to_return['getvars'] = ''
        return to_return
    except KeyError, AttributeError:
        return {}

register.inclusion_tag('pagination/pagination.html', takes_context=True)(
    paginate)
register.tag('autopaginate', do_autopaginate)
