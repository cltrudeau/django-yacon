# yacon.models.content.py
# blame ctrudeau chr(64) arsensa.com

import exceptions
from django.utils.safestring import mark_safe

# ============================================================================
# ContentHandler Objects
# ============================================================================

class ContentRenderingException(exceptions.Exception):
    pass

class PermissionHandler(object):
    VIEW_MODE = 1;
    EDIT_MODE = 2;

    def has_permission(self, request, mode):
        if mode == self.VIEW_MODE:
            return True
        elif mode == self.EDIT_MODE:
            return False
        
        return False

    def permission_denied_content(self, request):
        return '<p>Permission denied to this component</p>'

class ContentHandler(object):
    """Base class for content handlers, these specify how to retrieve content
    and make it available to the page renderers."""

    def __init__(self, block):
        self.block = block

    def internal_render(self):
        """Method that inheritors should over-ride to return content.  Called
        by render()"""
        pass

    def render(self):
        """Wraps internal_render() by adding information to any exceptions 
        caught and marking what is returned as safe."""
        try:
            return mark_safe(self.internal_render())
        except Exception, e:
            et = e.__class__.__name__
            ot = self.__class__.__name__
            msg = \
"""
An exception was caught while rendering using the user specified 
ContentHandler "%s".  The exception was: "%s" 
with the message:

%s

Typical causes are errors in the internal_render() method.
"""
            cre = ContentRenderingException(msg % (ot, et, e))
            raise cre


# ----------------------------------------------------------------------------
# System ContentHandlers

class FlatContent(ContentHandler):
    def internal_render(self):
        return self.block.content
