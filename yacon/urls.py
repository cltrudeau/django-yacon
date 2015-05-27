from django.conf.urls import patterns
from django.views.generic import TemplateView, RedirectView

from yacon import conf

urlpatterns = patterns('yacon.views.browser',
    (r'^ckeditor_browser/$', 'ckeditor_browser'),
    (r'^popup_browser/(.*)/$', 'popup_browser'),

    # left pane
    (r'^browser/tree_top/$', 'tree_top'),
    (r'^browser/sub_tree/$', 'sub_tree'),

    # right pane
    (r'^browser/root_control/(.*)/$', 'root_control'),
    (r'^browser/show_folder/$', 'show_folder'),
    (r'^browser/add_folder/(.*)/$', 'add_folder'),
    (r'^browser/remove_folder_warn/$', 'remove_folder_warn'),
    (r'^browser/remove_folder/$', 'remove_folder'),
    (r'^browser/remove_file/$', 'remove_file'),
    (r'^browser/image_edit/$', 'image_edit'),
    (r'^browser/image_edit_save/$', 'image_edit_save'),
    (r'^browser/file_expand/$', 'file_expand'),

    # upload 
    (r'^browser/upload_file/$', 'upload_file'),
    (r'^browser/user_upload_file/$', 'user_upload_file'),
)

urlpatterns += patterns('yacon.views.content',
    (r'^fetch_block/(\d+)/$', 'fetch_block'),
    (r'^fetch_owner/(\d+)/$', 'fetch_owner'),
    (r'^replace_block/$', 'replace_block'),
    (r'^replace_owner/$', 'replace_owner'),
    (r'^replace_title/$', 'replace_title'),
    (r'^flip_page_visible/$', 'flip_page_visible'),
    (r'^replace_metapage_perm/$', 'replace_metapage_perm'),
    (r'^replace_node_perm/$', 'replace_node_perm'),
    (r'^remove_page/(\d+)/$', 'remove_page'),
    (r'^create_page/(\d+)/([^/]*)/([^/]*)/(.*)/$', 'create_page'),
    (r'^create_page_from_node/(\d+)/(\d+)/([^/]*)/([^/]*)/$', 
        'create_page_from_node'),
)

urlpatterns += patterns('',
    (r'^denied/$', TemplateView.as_view(template_name='yacon/denied.html')),
)

if conf.site.static_serve and \
        (conf.nexus.enabled or conf.site.examples_enabled):
    # enable static serving of pages for nexus and examples
    import os
    cur_dir = os.path.dirname(__file__)
    static_root = os.path.join(cur_dir, 'static')

    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root':static_root}),
    )

if conf.nexus.enabled:
    # nexus tabs
    urlpatterns += patterns('yacon.views.nexus',
        (r'^$', RedirectView.as_view(url='/yacon/nexus/control_panel/')),
        (r'^nexus/$', RedirectView.as_view(url='/yacon/nexus/control_panel/')),

        # some of the JS is templated in order to be able to dynamically 
        #disable features
        (r'^nexus/site_control/$', TemplateView.as_view(
            template_name='yacon/nexus/templated_js/site_control.js',
            content_type='application/javascript')),
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
        (r'^nexus/control/list_languages/(\d+)/$', 'list_languages'),
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
        (r'^nexus/control/toggle_menuitem_requires_login/(\d+)/$',
            'toggle_menuitem_requires_login'),
        (r'^nexus/control/toggle_menuitem_requires_admin/(\d+)/$',
            'toggle_menuitem_requires_admin'),
        (r'^nexus/control/tags_control/$', 'tags_control'),
        (r'^nexus/control/tag_info/(\d+)/$', 'tag_info'),
        (r'^nexus/control/missing_tag_translations/(\d+)/$', 
            'missing_tag_translations'),
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
        (r'^nexus/control/add_link_menuitem/(\d+)/(.*)/(.*)/$',
            'add_link_menuitem'),
        (r'^nexus/control/add_header_menuitem/(\d+)/(.*)/(.*)/$',
            'add_header_menuitem'),
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

        # tag dialogs
        (r'^nexus/control/add_tag/(\d+)/(.*)/(.*)/$', 'add_tag'),
        (r'^nexus/control/add_tag_translation/(\d+)/(.*)/(.*)/$', 
            'add_tag_translation'),
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
        (r'^nexus/users_panel/$', RedirectView.as_view(
            url='/yacon/nexus/users/list_users/')),
    )

    urlpatterns += patterns('yacon.views.users_panel',
        (r'^nexus/users/list_users/$', 'list_users'),
        (r'^nexus/users/edit_user/(\d+)/$', 'edit_user'),
        (r'^nexus/users/add_user/$', 'add_user'),
        (r'^nexus/users/user_password/(\d+)/$', 'user_password'),
        (r'^nexus/users/su/(\d+)/$', 'switch_to_user'),
    )

    # -------------------
    # Uploads Panel
    urlpatterns += patterns('yacon.views.nexus',
        (r'^nexus/uploads_panel/$', 'uploads_panel'),
    )

if conf.site.examples_enabled:
    urlpatterns += patterns('',
        (r'^(examples/uploads/.+\.html)$', TemplateView.as_view()),
    )
