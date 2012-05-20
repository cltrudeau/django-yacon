# yacon.models.content.py
# blame ctrudeau chr(64) arsensa.com

import exceptions, logging
from django.template import RequestContext, Template
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

# ============================================================================
# PermissionHandler Objects
# ============================================================================

class PermissionHandler(object):
    """Base class for permissions used by ContentHandler.  Default denies all
    permissions to everyone."""
    CAN_VIEW = 1;
    CAN_EDIT = 2;

    def has_permission(self, request, mode):
        logger.debug('returning False')
        return False

    def permission_denied_content(self, request):
        logger.debug('returning default denied message')
        return '<p>Permission denied to this component</p>'


class AlwaysYesPermissionHandler(PermissionHandler):
    """PermissionHandler that grants everyone permission always.  Probably
    shouldn't be used in production, good for testing."""
    def has_permission(self, request, mode): 
        logger.debug('returning True')
        return True


# ============================================================================
# ContentHandler Objects
# ============================================================================

class ContentRenderingException(exceptions.Exception):
    pass


class ContentHandler(object):
    """Base class for content handlers, these specify how to retrieve content
    and make it available to the page renderers."""

    def __init__(self, block_type, parms):
        self.parms = parms
        self.block_type = block_type

    def internal_render(self, request, block):
        """Method that inheritors should over-ride to return content.  Called
        by render()"""
        pass

    def render(self, request, block):
        """Wraps internal_render() by adding information to any exceptions 
        caught and marking what is returned as safe."""
        try:
            return mark_safe(self.internal_render(request, block))
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
""" % (ot, et, e)

            cre = ContentRenderingException(msg)
            raise cre


# ----------------------------------------------------------------------------
# System ContentHandlers

class FlatContent(ContentHandler):
    """ContentHandler for content that requires no permission checking or
    other work, essentially just outputs what is in the db for the block"""
    def internal_render(self, request, block):
        logger.debug('returning content')
        c = RequestContext(request)
        t = Template(block.content)
        return t.render(c)


class EditableContent(ContentHandler):
    """ContentHandler for user editable content.  Rendering depends on a
    PermissionHandler as to what is presented if anything at all.  The 
    PermissionHandler class to instantiate is passed in as part of the 
    parent's parameters."""

    def internal_render(self, request, uri, node, slugs, block):
        perms = self.parms['permission_class']()

        if request.method == 'POST':
            # attempt to edit content, check for permissions
            if not perms.has_permission(request, perms.CAN_EDIT):
                logger.debug('returning permission denied')
                return perms.permission_denied_content(request)

            # has edit permission
            block.is_editable = True
            logger.debug('returning content with editable True')
            return block.content

        # else -- request.method == 'GET'
        if not perms.has_permission(request, perms.CAN_VIEW):
            logger.debug('returning permission denied')
            return perms.permission_denied_content(request)

        logger.debug('returning content with editable False')
        return block.content


class AjaxEditableContent(ContentHandler):
    """This ContentHandler allows for fetching and editing of the content through Ajax
    calls.  The user's permission level is checked and determines whether they can see
    and/or edit the block.  If the user has edit permissions then an Edit link is added
    to the content along with a block identifier.
    """

    def internal_render(self, request, block):
        original = super(EditableContent, self).internal_render(request, uri,
            node, slugs)

        content = \
"""<div block_id="%s">
%s
</div>""" % (block.id, original)

        logger.debug('returning content')
        return content
