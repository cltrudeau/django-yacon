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
        (r'^nexus/ajax_page_info/$', 'ajax_page_info'),
        (r'^nexus/ajax_metapage_info/(\d+)/$', 'ajax_metapage_info'),
        (r'^nexus/ajax_node_info/(\d+)/$', 'ajax_node_info'),
        (r'^nexus/ajax_site_info/(\d+)/$', 'ajax_site_info'),
        (r'^nexus/ajax_get_sites/$', 'ajax_get_sites'),
        (r'^nexus/ajax_site_tree/(\d+)/$', 'ajax_site_tree'),
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
