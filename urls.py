from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),

    (r'^ajax_submit/$', 'yacon.views.user.ajax_submit'),
)

if settings.YACON_STATIC_SERVE and (settings.YACON_NEXUS_ENABLED or 
    settings.YACON_EXAMPLES_ENABLED):
    # enable static serving of pages for nexus and examples
    import os
    cur_dir = os.path.dirname(__file__)
    static_root = os.path.join(cur_dir, 'static')

    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root':static_root}),
    )

if settings.YACON_NEXUS_ENABLED:
    urlpatterns += patterns('yacon.views.nexus',
        (r'^$', 'control_panel'),
        (r'^nexus/$', 'control_panel'),
        (r'^nexus/control_panel/$', 'control_panel'),

        # control panel display items
        (r'^nexus/page_info/$', 'page_info'),
        (r'^nexus/metapage_info/(\d+)/$', 'metapage_info'),
        (r'^nexus/node_info/(\d+)/$', 'node_info'),
        (r'^nexus/site_info/(\d+)/$', 'site_info'),
        (r'^nexus/get_sites/$', 'get_sites'),
        (r'^nexus/full_tree/(\d+)/$', 'full_tree'),

        # control panel dialog items
        (r'^nexus/remove_folder_warn/(\d+)/$', 'remove_folder_warn'),
    )

if settings.YACON_TESTS_ENABLED:
    urlpatterns += patterns('',
        (r'^tests/$', direct_to_template, {'template':'tests/index.html'}),
    )

if settings.YACON_EXAMPLES_ENABLED:
#    urlpatterns += patterns('',
#        (r'^content_listing/$', 'yacon.views.user.content_listing'),
#    )
    pass
