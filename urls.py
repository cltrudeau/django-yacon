from django.conf import settings
from django.conf.urls.defaults import patterns
from django.views.generic.simple import redirect_to, direct_to_template

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
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
    # nexus tabs
    urlpatterns += patterns('yacon.views.nexus',
        (r'^$', redirect_to, {'url':'/yacon/nexus/control_panel/'}),
        (r'^nexus/$', redirect_to, {'url':'/yacon/nexus/control_panel/'}),
        (r'^nexus/control_panel/$', 'control_panel'),
        (r'^nexus/config/$', 'config'),
        (r'^nexus/js/site_control.js/$', direct_to_template, 
            {'template':'nexus/js/site_control.js',
            'mimetype':'application/javascript'}),
        (r'^nexus/list_users/$', 'list_users'),
        (r'^nexus/edit_user/(\d+)/$', 'edit_user'),
        (r'^nexus/add_user/$', 'add_user'),
        (r'^nexus/user_password/(\d+)/$', 'user_password'),
    )

    # control panel, left pane
    urlpatterns += patterns('yacon.views.left_control',
        (r'^nexus/get_sites/$', 'get_sites'),
        (r'^nexus/full_tree/(\d+)/$', 'full_tree'),
        (r'^nexus/full_tree_default_site/$', 'full_tree_default_site'),
        (r'^nexus/sub_tree/$', 'sub_tree'),
    )

    # control panel, right pane
    urlpatterns += patterns('yacon.views.right_control',
        (r'^nexus/site_info/(\d+)/$', 'site_info'),
        (r'^nexus/node_info/(\d+)/$', 'node_info'),
        (r'^nexus/metapage_info/(\d+)/$', 'metapage_info'),
        (r'^nexus/menus_control/$', 'menus_control'),
        (r'^nexus/menu_info/(\d+)/$', 'menu_info'),
        (r'^nexus/menuitem_info/(\d+)/$', 'menuitem_info'),
        (r'^nexus/missing_node_translations/(\d+)/$', 
            'missing_node_translations'),
        (r'^nexus/missing_metapage_translations/(\d+)/$', 
            'missing_metapage_translations'),
        (r'^nexus/missing_menuitem_translations/(\d+)/$', 
            'missing_menuitem_translations'),
        (r'^nexus/move_menuitem_out/(\d+)/$', 'move_menuitem_out'),
        (r'^nexus/move_menuitem_up/(\d+)/$', 'move_menuitem_up'),
        (r'^nexus/move_menuitem_down/(\d+)/$', 'move_menuitem_down'),
    )

    # settings tab
    urlpatterns += patterns('yacon.views.settings_tab',
        (r'^nexus/add_language/(.*)/(.*)/$', 'add_language'),
    )

    # control panel, dialogs
    urlpatterns += patterns('yacon.views.dialogs',
        # node dialogs
        (r'^nexus/remove_folder_warn/(\d+)/$', 'remove_folder_warn'),
        (r'^nexus/remove_folder/(\d+)/$', 'remove_folder'),
        (r'^nexus/add_folder/(\d+)/(.*)/(.*)/$', 'add_folder'),
        (r'^nexus/add_page/(\d+)/(\d+)/(.*)/(.*)/$', 'add_page'),
        (r'^nexus/add_path/(\d+)/(.*)/(.*)/(.*)/$', 'add_path'),
        (r'^nexus/remove_path_warn/(\d+)/$', 'remove_path_warn'),
        (r'^nexus/remove_path/(\d+)/$', 'remove_path'),
        (r'^nexus/edit_path_warn/(\d+)/$', 'edit_path_warn'),
        (r'^nexus/edit_path/(\d+)/(.*)/(.*)/$', 'edit_path'),

        # metapage dialogs
        (r'^nexus/page_types/$', 'page_types'),
        (r'^nexus/remove_page_warn/(\d+)/$', 'remove_page_warn'),
        (r'^nexus/remove_page/(\d+)/$', 'remove_page'),
        (r'^nexus/add_translation/(\d+)/(.*)/(.*)/(.*)/$', 'add_translation'),
        (r'^nexus/make_default_metapage/(\d+)/$', 'make_default_metapage'),
        (r'^nexus/remove_page_translation/(\d+)/$', 'remove_page_translation'),
        (r'^nexus/menu_listing/(\d+)/$', 'menu_listing'),
        (r'^nexus/add_menuitem/(\d+)/(\d+)/(.*)/$', 'add_menuitem'),

        # site dialogs
        (r'^nexus/missing_site_languages/(\d+)/$', 'missing_site_languages'),
        (r'^nexus/site_languages/(\d+)/$', 'site_languages'),
        (r'^nexus/all_languages/$', 'all_languages'),
        (r'^nexus/add_site_lang/(\d+)/(.*)/$', 'add_site_lang'),
        (r'^nexus/edit_site/(\d+)/(.*)/(.*)/(.*)/$', 'edit_site'),
        (r'^nexus/add_site/(.*)/(.*)/(.*)/$', 'add_site'),

        # menu dialogs
        (r'^nexus/add_menu/(\d+)/(.*)/$', 'add_menu'),
        (r'^nexus/remove_menu_warn/(\d+)/$', 'remove_menu_warn'),
        (r'^nexus/remove_menu/(\d+)/$', 'remove_menu'),

        # menuitem dialogs
        (r'^nexus/remove_menuitem_translation/(\d+)/$', 
            'remove_menuitem_translation'),
        (r'^nexus/remove_menuitem_warn/(\d+)/$', 'remove_menuitem_warn'),
        (r'^nexus/remove_menuitem/(\d+)/$', 'remove_menuitem'),
        (r'^nexus/add_menuitem_translation/(\d+)/(.*)/(.*)/$', 
            'add_menuitem_translation'),
        (r'^nexus/rename_menuitem_translation/(\d+)/(.*)/$', 
            'rename_menuitem_translation'),
        (r'^nexus/create_menuitem_translation/(\d+)/(.*)/(.*)/$', 
            'create_menuitem_translation'),
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
