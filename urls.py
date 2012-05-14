from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to, direct_to_template

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
        (r'^$', redirect_to, {'url':'/yacon/nexus/control_panel/'}),
        (r'^nexus/$', redirect_to, {'url':'/yacon/nexus/control_panel/'}),
        (r'^nexus/control_panel/$', 'control_panel'),
        (r'^nexus/config/$', 'config'),

        # control panel display items
        (r'^nexus/metapage_info/(\d+)/$', 'metapage_info'),
        (r'^nexus/node_info/(\d+)/$', 'node_info'),
        (r'^nexus/site_info/(\d+)/$', 'site_info'),
        (r'^nexus/get_sites/$', 'get_sites'),
        (r'^nexus/page_types/$', 'page_types'),
        (r'^nexus/full_tree/(\d+)/$', 'full_tree'),
        (r'^nexus/full_tree_default_site/$', 'full_tree_default_site'),

        # control panel dialog items
        (r'^nexus/remove_folder_warn/(\d+)/$', 'remove_folder_warn'),
        (r'^nexus/remove_folder/(\d+)/$', 'remove_folder'),
        (r'^nexus/add_folder/(\d+)/(.*)/(.*)/$', 'add_folder'),
        (r'^nexus/add_page/(\d+)/(\d+)/(.*)/(.*)/$', 'add_page'),
        (r'^nexus/remove_page_warn/(\d+)/$', 'remove_page_warn'),
        (r'^nexus/remove_page/(\d+)/$', 'remove_page'),
        (r'^nexus/missing_node_translations/(\d+)/$', 
            'missing_node_translations'),
        (r'^nexus/missing_metapage_translations/(\d+)/$', 
            'missing_metapage_translations'),
        (r'^nexus/add_translation/(\d+)/(.*)/(.*)/(.*)/$', 'add_translation'),
        (r'^nexus/add_path/(\d+)/(.*)/(.*)/(.*)/$', 'add_path'),
        (r'^nexus/remove_path_warn/(\d+)/$', 'remove_path_warn'),
        (r'^nexus/remove_path/(\d+)/$', 'remove_path'),
        (r'^nexus/edit_path_warn/(\d+)/$', 'edit_path_warn'),
        (r'^nexus/edit_path/(\d+)/(.*)/(.*)/$', 'edit_path'),
        (r'^nexus/make_default_metapage/(\d+)/$', 'make_default_metapage'),
        (r'^nexus/remove_page_translation/(\d+)/$', 'remove_page_translation'),
        (r'^nexus/missing_site_languages/(\d+)/$', 'missing_site_languages'),
        (r'^nexus/site_languages/(\d+)/$', 'site_languages'),
        (r'^nexus/all_languages/$', 'all_languages'),
        (r'^nexus/add_site_lang/(\d+)/(.*)/$', 'add_site_lang'),
        (r'^nexus/edit_site/(\d+)/(.*)/(.*)/(.*)/$', 'edit_site'),
        (r'^nexus/add_site/(.*)/(.*)/(.*)/$', 'add_site'),

        # settings page dialog items
        (r'^nexus/add_language/(.*)/(.*)/$', 'add_language'),
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
