# yacon.admin.py

import logging

from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from yacon.models.groupsq import GroupOfGroups
from yacon.models.hierarchy import Node
from yacon.models.pages import MetaPage, Page

logger = logging.getLogger(__name__)

# =============================================================================
# Admin Classes
# =============================================================================

# =============================================================================
# Add Modules To Admin

@admin.register(GroupOfGroups)
class GroupOfGroupsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(MetaPage)
class MetaPageAdmin(admin.ModelAdmin):
    list_display = ('id', 'self_node', 'self_page_type', 'alias', 
        'is_node_default', 'owner', 'permission', 'hidden', 'self_pages')

    def self_pages(self, obj):
        pages = []
        for page in obj.page_set.all():
            pages.append('<a href="/admin/yacon/page/%s/">%s</a>' % (page.id,
                page.title))

        return ','.join(pages)
    self_pages.allow_tags = True

    def self_node(self, obj):
        return '<a href="/admin/yacon/node/%s/">id=%s:%s:%s</a>' % (
            obj.node.id, obj.node.id, obj.node.name, obj.node.slug)
    self_node.allow_tags = True

    def self_page_type(self, obj):
        return obj.page_type.name


@admin.register(Node)
class NodeAdmin(TreeAdmin):
    form = movenodeform_factory(Node)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'language', 'self_slug', 'title')

    def self_slug(self, obj):
        return '<a href="%s">%s</a>' % (obj.uri, obj.slug)
    self_slug.allow_tags = True
