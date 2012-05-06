# yacon.admin.py

import logging

from django.contrib import admin

from yacon.models.pages import MetaPage

logger = logging.getLogger(__name__)

# =============================================================================
# Admin Classes
# =============================================================================

# =============================================================================
# Add Modules To Admin

admin.site.register(MetaPage)
