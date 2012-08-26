# yacon.utils.py
import logging, json, inspect

from django.http import HttpResponse

logger = logging.getLogger(__name__)

# ============================================================================

# get_user_attributes
# 
# borrowed and modified from: 
#   http://stackoverflow.com/questions/4241171/inspect-python-class-attributes

def get_user_attributes(obj, exclude_methods=True):
    """Returns a list of non-system attributes for an object.

    :param obj: object or class to inspect
    :param exclude_methods: [optional] do not include callable methods in the
        returned list, defaults to True
    
    :returns: list of non-system attributes of an object or class
    """
    base_attributes = dir(type('dummy', (object,), {}))
    attributes = dir(obj)
    results = []
    for attribute in attributes:
        try:
            if attribute in base_attributes \
                    or (exclude_methods and callable(getattr(obj, attribute))):
                continue
            results.append(attribute)
        except AttributeError:
            # some kinds of access cause problems, ignore them
            pass

    return results


# Enum
#
# borrowed and modified from:
#  http://tomforb.es/using-python-metaclasses-to-make-awesome-django-model-field-choices

class Enum(object):
    """A tuple of tuples pattern of (id, string) is common in django for
    choices fields, etc.  This object inspects its own members (i.e. the
    inheritors) and produces the corresponding tuples.

    Example:

    class Colours(Enum):
        RED = 'r'
        BLUE = 'b', 'Blueish'

    >> Colours.RED
    'r'
    >> list(Colours)
    [('r', 'Red'), ('b', 'Blueish')]
    """
    class __metaclass__(type):
        def __init__(self, *args, **kwargs):
            self._data = []
            for name, value in inspect.getmembers(self):
                if not name.startswith('_') and not inspect.ismethod(value):
                    if isinstance(value, tuple) and len(value) > 1:
                        data = value
                    else:
                        pieces = [x.capitalize() for x in name.split('_')]
                        data = (value, ' '.join(pieces))
                    self._data.append(data)
                    setattr(self, name, data[0])

            self._hash = dict(self._data)

        def __iter__(self):
            for value, data in self._data:
                yield (value, data)

    @classmethod
    def get_value(self, key):
        return self._hash[key]


class JSONResponse(HttpResponse):
    def __init__(self, obj, **kwargs):
        extra_headers = kwargs.pop('extra_headers', {})
        kwargs['mimetype'] = 'application/json'
        super(JSONResponse, self).__init__(json.dumps(obj), **kwargs)

        for key, value in extra_headers.items():
            self[key] = value
