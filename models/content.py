# yacon.models.content.py
# blame ctrudeau chr(64) arsensa.com

import exceptions, logging
from django.utils.safestring import mark_safe

# ============================================================================
# PermissionHandler Objects
# ============================================================================

class PermissionHandler(object):
    """Base class for permissions used by ContentHandler.  Default denies all
    permissions to everyone."""
    CAN_VIEW = 1;
    CAN_EDIT = 2;

    def has_permission(self, request, mode):
        logging.debug('returning False')
        return False

    def permission_denied_content(self, request):
        logging.debug('returning default denied message')
        return '<p>Permission denied to this component</p>'


class AlwaysYesPermissionHandler(PermissionHandler):
    """PermissionHandler that grants everyone permission always.  Probably
    shouldn't be used in production, good for testing."""
    def has_permission(self, request, mode): 
        logging.debug('returning True')
        return True


# ============================================================================
# ContentHandler Objects
# ============================================================================

class ContentRenderingException(exceptions.Exception):
    pass


class ContentHandler(object):
    """Base class for content handlers, these specify how to retrieve content
    and make it available to the page renderers."""

    def __init__(self, block, parms):
        self.parms = parms
        self.block = block

    def internal_render(self, request, uri, node, slugs):
        """Method that inheritors should over-ride to return content.  Called
        by render()"""
        pass

    def render(self, request, uri, node, slugs):
        """Wraps internal_render() by adding information to any exceptions 
        caught and marking what is returned as safe."""
        try:
            return mark_safe(self.internal_render(request, uri, node, slugs))
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
    """ContentHandler for content that requires no permission checking or
    other work, essentially just outputs what is in the db for the block"""
    def internal_render(self, request, uri, node, slugs):
        logging.debug('returning content')
        return self.block.content


class EditableContent(ContentHandler):
    """ContentHandler for user editable content.  Rendering depends on a
    PermissionHandler as to what is presented if anything at all.  The 
    PermissionHandler class to instantiate is passed in as part of the 
    parent's parameters."""

    def internal_render(self, request, uri, node, slugs):
        perms = self.parms['permission_class']()

        if request.method == 'POST':
            # attempt to edit content, check for permissions
            if not perms.has_permission(request, perms.CAN_EDIT):
                logging.debug('returning permission denied')
                return perms.permission_denied_content(request)

            # has edit permission
            self.block.is_editable = True
            logging.debug('returning content with editable True')
            return self.block.content

        # else -- request.method == 'GET'
        if not perms.has_permission(request, perms.CAN_VIEW):
            logging.debug('returning permission denied')
            return perms.permission_denied_content(request)

        logging.debug('returning content with editable False')
        return self.block.content


class AjaxEditableContent(EditableContent):
    """Same as EditableContent except that it wraps all block content in a 
    <div> to make it easier to manipulate with the ajax_submit view"""

    def internal_render(self, request, uri, node, slugs):
        original = super(EditableContent, self).internal_render(request, uri,
            node, slugs)

        content = \
"""<div block_id="%s">
%s
</div>""" % (self.block.id, original)

        logging.debug('returning content')
        return content
