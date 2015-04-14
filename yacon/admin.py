# yacon.admin.py

import logging

from django.contrib import admin

from yacon.models.pages import MetaPage
from yacon.models.groupsq import GroupOfGroups

logger = logging.getLogger(__name__)

# =============================================================================
# Admin Classes
# =============================================================================

# =============================================================================
# Add Modules To Admin

admin.site.register(MetaPage)

@admin.register(GroupOfGroups)
class GroupOfGroupsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
