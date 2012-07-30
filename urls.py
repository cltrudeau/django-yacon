from django.conf import settings
from django.conf.urls.defaults import patterns
from django.views.generic.simple import redirect_to, direct_to_template

from yacon.conf import site, nexus

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)

if site('static_serve') and (nexus('enabled') or site('examples_enabled')):
    # enable static serving of pages for nexus and examples
    import os
    cur_dir = os.path.dirname(__file__)
    static_root = os.path.join(cur_dir, 'static')

    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root':static_root}),
    )

if nexus('enabled'):
    # nexus tabs
    urlpatterns += patterns('yacon.views.nexus',
        (r'^$', redirect_to, {'url':'/yacon/nexus/control_panel/'}),
        (r'^nexus/$', redirect_to, {'url':'/yacon/nexus/control_panel/'}),

        # some of the JS is templated in order to be able to dynamically 
        #disable features
        (r'^nexus/site_control/$', direct_to_template, 
            {'template':'nexus/templated_js/site_control.js',
            'mimetype':'application/javascript'}),
    )

    # -------------------
    # Control Panel
    urlpatterns += patterns('yacon.views.nexus',
        (r'^nexus/control_panel/$', 'control_panel'),
    )

    # control panel, left pane
    urlpatterns += patterns('yacon.views.left_control',
        (r'^nexus/control/get_sites/$', 'get_sites'),
        (r'^nexus/control/tree_top/(\d+)/$', 'tree_top'),
        (r'^nexus/control/tree_top_default_site/$', 'tree_top_default_site'),
        (r'^nexus/control/sub_tree/$', 'sub_tree'),
    )

    # control panel, right pane
    urlpatterns += patterns('yacon.views.right_control',
        (r'^nexus/control/site_info/(\d+)/$', 'site_info'),
        (r'^nexus/control/node_info/(\d+)/$', 'node_info'),
        (r'^nexus/control/metapage_info/(\d+)/$', 'metapage_info'),
        (r'^nexus/control/menus_control/$', 'menus_control'),
        (r'^nexus/control/menu_info/(\d+)/$', 'menu_info'),
        (r'^nexus/control/menuitem_info/(\d+)/$', 'menuitem_info'),
        (r'^nexus/control/missing_node_translations/(\d+)/$', 
            'missing_node_translations'),
        (r'^nexus/control/missing_metapage_translations/(\d+)/$', 
            'missing_metapage_translations'),
        (r'^nexus/control/missing_menuitem_translations/(\d+)/$', 
            'missing_menuitem_translations'),
        (r'^nexus/control/move_menuitem_out/(\d+)/$', 'move_menuitem_out'),
        (r'^nexus/control/move_menuitem_up/(\d+)/$', 'move_menuitem_up'),
        (r'^nexus/control/move_menuitem_down/(\d+)/$', 'move_menuitem_down'),
    )




    # control panel, dialogs
    urlpatterns += patterns('yacon.views.dialogs',
        # node dialogs
        (r'^nexus/control/remove_folder_warn/(\d+)/$', 'remove_folder_warn'),
        (r'^nexus/control/remove_folder/(\d+)/$', 'remove_folder'),
        (r'^nexus/control/add_folder/(\d+)/(.*)/(.*)/$', 'add_folder'),
        (r'^nexus/control/add_page/(\d+)/(\d+)/(.*)/(.*)/$', 'add_page'),
        (r'^nexus/control/add_path/(\d+)/(.*)/(.*)/(.*)/$', 'add_path'),
        (r'^nexus/control/remove_path_warn/(\d+)/$', 'remove_path_warn'),
        (r'^nexus/control/remove_path/(\d+)/$', 'remove_path'),
        (r'^nexus/control/edit_path_warn/(\d+)/$', 'edit_path_warn'),
        (r'^nexus/control/edit_path/(\d+)/(.*)/(.*)/$', 'edit_path'),

        # metapage dialogs
        (r'^nexus/control/page_types/$', 'page_types'),
        (r'^nexus/control/remove_page_warn/(\d+)/$', 'remove_page_warn'),
        (r'^nexus/control/remove_page/(\d+)/$', 'remove_page'),
        (r'^nexus/control/add_translation/(\d+)/(.*)/(.*)/(.*)/$', 
            'add_translation'),
        (r'^nexus/control/make_default_metapage/(\d+)/$', 
            'make_default_metapage'),
        (r'^nexus/control/remove_page_translation/(\d+)/$', 
            'remove_page_translation'),
        (r'^nexus/control/menu_listing/(\d+)/$', 'menu_listing'),
        (r'^nexus/control/add_menuitem/(\d+)/(\d+)/(.*)/$', 'add_menuitem'),

        # site dialogs
        (r'^nexus/control/missing_site_languages/(\d+)/$', 
            'missing_site_languages'),
        (r'^nexus/control/site_languages/(\d+)/$', 'site_languages'),
        (r'^nexus/control/all_languages/$', 'all_languages'),
        (r'^nexus/control/add_site_lang/(\d+)/(.*)/$', 'add_site_lang'),
        (r'^nexus/control/edit_site/(\d+)/(.*)/(.*)/(.*)/$', 'edit_site'),
        (r'^nexus/control/add_site/(.*)/(.*)/(.*)/$', 'add_site'),

        # menu dialogs
        (r'^nexus/control/add_menu/(\d+)/(.*)/$', 'add_menu'),
        (r'^nexus/control/remove_menu_warn/(\d+)/$', 'remove_menu_warn'),
        (r'^nexus/control/remove_menu/(\d+)/$', 'remove_menu'),

        # menuitem dialogs
        (r'^nexus/control/remove_menuitem_translation/(\d+)/$', 
            'remove_menuitem_translation'),
        (r'^nexus/control/remove_menuitem_warn/(\d+)/$', 
            'remove_menuitem_warn'),
        (r'^nexus/control/remove_menuitem/(\d+)/$', 'remove_menuitem'),
        (r'^nexus/control/add_menuitem_translation/(\d+)/(.*)/(.*)/$', 
            'add_menuitem_translation'),
        (r'^nexus/control/rename_menuitem_translation/(\d+)/(.*)/$', 
            'rename_menuitem_translation'),
        (r'^nexus/control/create_menuitem_translation/(\d+)/(.*)/(.*)/$', 
            'create_menuitem_translation'),
    )

    # -------------------
    # Settings Panel
    urlpatterns += patterns('yacon.views.nexus',
        (r'^nexus/config_panel/$', 'config_panel'),
    )

    urlpatterns += patterns('yacon.views.config_panel',
        (r'^nexus/config/add_language/(.*)/(.*)/$', 'add_language'),
    )

    # -------------------
    # Users Panel
    urlpatterns += patterns('yacon.views.nexus',
        (r'^nexus/users_panel/$', redirect_to, 
            {'url':'/yacon/nexus/users/list_users/'}),
    )

    urlpatterns += patterns('yacon.views.users_panel',
        (r'^nexus/users/list_users/$', 'list_users'),
        (r'^nexus/users/edit_user/(\d+)/$', 'edit_user'),
        (r'^nexus/users/add_user/$', 'add_user'),
        (r'^nexus/users/user_password/(\d+)/$', 'user_password'),
    )

    # -------------------
    # Uploads Panel
    urlpatterns += patterns('yacon.views.nexus',
        (r'^nexus/uploads_panel/$', 'uploads_panel'),
    )

    urlpatterns += patterns('yacon.views.uploads_panel',
        # left pane
        (r'^nexus/uploads/tree_top/$', 'tree_top'),
        (r'^nexus/uploads/sub_tree/$', 'sub_tree'),

        # right pane
        (r'^nexus/uploads/root_control/(.*)/$', 'root_control'),
        (r'^nexus/uploads/folder_info/(.*)/$', 'folder_info'),
        (r'^nexus/uploads/add_to_database/(.*)/$', 'add_to_database'),
        (r'^nexus/uploads/add_folder/(.*)/(.*)/$', 'add_folder'),
        (r'^nexus/uploads/remove_folder_warn/(.*)/$', 'remove_folder_warn'),
        (r'^nexus/uploads/remove_folder/(.*)/$', 'remove_folder'),
        (r'^nexus/uploads/list_owners/$', 'list_owners'),
        (r'^nexus/uploads/change_owner/(.*)/(\d+)/$', 'change_owner'),
        (r'^nexus/uploads/remove_file/(.*)/$', 'remove_file'),

        # upload 
        (r'^nexus/uploads/upload_file/$', 'upload_file'),
        (r'^nexus/uploads/user_upload_file/$', 'user_upload_file'),
        (r'^nexus/uploads/upload_image/$', 'upload_image'),
    )

if site('examples_enabled'):
    urlpatterns += patterns('',
        (r'^(examples/uploads/.+\.html)$', direct_to_template),
    )
