# yacon.utils.py
import logging, json

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


class JSONResponse(HttpResponse):
    def __init__(self, *args, **kwargs):
        if 'mimetype' not in kwargs:
            kwargs['mimetype'] = 'application/json'
        local_args = list(args)
        local_args[0] = json.dumps(args[0])

        super(JSONResponse, self).__init__(*local_args, **kwargs)
