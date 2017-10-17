from django.conf.urls import url
from django.views.generic import TemplateView, RedirectView

from yacon import conf
from yacon.views import browser
from yacon.views import content

urlpatterns = [
    url(r'^ckeditor_browser/$', browser.ckeditor_browser),
    url(r'^popup_browser/(.*)/$', browser.popup_browser),

    # left pane
    url(r'^browser/tree_top/$', browser.tree_top),
    url(r'^browser/sub_tree/$', browser.sub_tree),

    # right pane
    url(r'^browser/root_control/(.*)/$', browser.root_control),
    url(r'^browser/show_folder/$', browser.show_folder),
    url(r'^browser/add_folder/(.*)/$', browser.add_folder),
    url(r'^browser/remove_folder_warn/$', browser.remove_folder_warn),
    url(r'^browser/remove_folder/$', browser.remove_folder),
    url(r'^browser/remove_file/$', browser.remove_file),
    url(r'^browser/image_edit/$', browser.image_edit),
    url(r'^browser/image_edit_save/$', browser.image_edit_save),
    url(r'^browser/file_expand/$', browser.file_expand),

    # upload 
    url(r'^browser/upload_file/$', browser.upload_file),
    url(r'^browser/user_upload_file/$', browser.user_upload_file),
]

urlpatterns += [
    url(r'^fetch_block/(\d+)/$', content.fetch_block),
    url(r'^fetch_owner/(\d+)/$', content.fetch_owner),
    url(r'^replace_block/$', content.replace_block),
    url(r'^replace_owner/$', content.replace_owner),
    url(r'^replace_title/$', content.replace_title),
    url(r'^flip_page_visible/$', content.flip_page_visible),
    url(r'^replace_metapage_perm/$', content.replace_metapage_perm),
    url(r'^replace_node_perm/$', content.replace_node_perm),
    url(r'^remove_page/(\d+)/$', content.remove_page),
    url(r'^create_page/(\d+)/([^/]*)/([^/]*)/(.*)/$', content.create_page),
    url(r'^create_page_from_node/(\d+)/(\d+)/([^/]*)/([^/]*)/$', 
        content.create_page_from_node),
]

urlpatterns += [
    url(r'^denied/$', TemplateView.as_view(template_name='yacon/denied.html')),
]

if conf.site.static_serve and \
        (conf.nexus.enabled or conf.site.examples_enabled):
    # enable static serving of pages for nexus and examples
    import os
    cur_dir = os.path.dirname(__file__)
    static_root = os.path.join(cur_dir, 'static')

    urlpatterns += [
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root':static_root}),
    ]

if conf.nexus.enabled:
    # nexus tabs
    urlpatterns += [
        url(r'^$', RedirectView.as_view(url='/yacon/nexus/control_panel/')),
        url(r'^nexus/$', RedirectView.as_view(
            url='/yacon/nexus/control_panel/')),

        # some of the JS is templated in order to be able to dynamically 
        #disable features
        url(r'^nexus/site_control/$', TemplateView.as_view(
            template_name='yacon/nexus/templated_js/site_control.js',
            content_type='application/javascript')),
    ]

    # -------------------
    # Control Panel
    from yacon.views import nexus 
    urlpatterns += [
        url(r'^nexus/control_panel/$', nexus.control_panel),
    ]

    # control panel, left pane
    from yacon.views import left_control 
    urlpatterns += [
        url(r'^nexus/control/get_sites/$', left_control.get_sites),
        url(r'^nexus/control/tree_top/(\d+)/$', left_control.tree_top),
        url(r'^nexus/control/tree_top_default_site/$', 
            left_control.tree_top_default_site),
        url(r'^nexus/control/sub_tree/$', left_control.sub_tree),
    ]

    # control panel, right pane
    from yacon.views import right_control 
    urlpatterns += [
        url(r'^nexus/control/site_info/(\d+)/$', right_control.site_info),
        url(r'^nexus/control/node_info/(\d+)/$', right_control.node_info),
        url(r'^nexus/control/metapage_info/(\d+)/$', 
            right_control.metapage_info),
        url(r'^nexus/control/list_languages/(\d+)/$', 
            right_control.list_languages),
        url(r'^nexus/control/menus_control/$', right_control.menus_control),
        url(r'^nexus/control/menu_info/(\d+)/$', right_control.menu_info),
        url(r'^nexus/control/menuitem_info/(\d+)/$', 
            right_control.menuitem_info),
        url(r'^nexus/control/missing_node_translations/(\d+)/$', 
            right_control.missing_node_translations),
        url(r'^nexus/control/missing_metapage_translations/(\d+)/$', 
            right_control.missing_metapage_translations),
        url(r'^nexus/control/missing_menuitem_translations/(\d+)/$', 
            right_control.missing_menuitem_translations),
        url(r'^nexus/control/move_menuitem_out/(\d+)/$', 
            right_control.move_menuitem_out),
        url(r'^nexus/control/move_menuitem_up/(\d+)/$', 
            right_control.move_menuitem_up),
        url(r'^nexus/control/move_menuitem_down/(\d+)/$', 
            right_control.move_menuitem_down),
        url(r'^nexus/control/toggle_menuitem_requires_login/(\d+)/$',
            right_control.toggle_menuitem_requires_login),
        url(r'^nexus/control/toggle_menuitem_requires_admin/(\d+)/$',
            right_control.toggle_menuitem_requires_admin),
        url(r'^nexus/control/tags_control/$', right_control.tags_control),
        url(r'^nexus/control/tag_info/(\d+)/$', right_control.tag_info),
        url(r'^nexus/control/missing_tag_translations/(\d+)/$', 
            right_control.missing_tag_translations),
    ]

    # control panel, dialogs
    from yacon.views import dialogs 
    urlpatterns += [
        # node dialogs
        url(r'^nexus/control/remove_folder_warn/(\d+)/$', 
            dialogs.remove_folder_warn),
        url(r'^nexus/control/remove_folder/(\d+)/$', dialogs.remove_folder),
        url(r'^nexus/control/add_folder/(\d+)/(.*)/(.*)/$', dialogs.add_folder),
        url(r'^nexus/control/add_page/(\d+)/(\d+)/(.*)/(.*)/$', 
            dialogs.add_page),
        url(r'^nexus/control/add_path/(\d+)/(.*)/(.*)/(.*)/$', 
            dialogs.add_path),
        url(r'^nexus/control/remove_path_warn/(\d+)/$', 
            dialogs.remove_path_warn),
        url(r'^nexus/control/remove_path/(\d+)/$', dialogs.remove_path),
        url(r'^nexus/control/edit_path_warn/(\d+)/$', dialogs.edit_path_warn),
        url(r'^nexus/control/edit_path/(\d+)/(.*)/(.*)/$', dialogs.edit_path),

        # metapage dialogs
        url(r'^nexus/control/page_types/$', dialogs.page_types),
        url(r'^nexus/control/remove_page_warn/(\d+)/$', 
            dialogs.remove_page_warn),
        url(r'^nexus/control/remove_page/(\d+)/$', dialogs.remove_page),
        url(r'^nexus/control/add_translation/(\d+)/(.*)/(.*)/(.*)/$', 
            dialogs.add_translation),
        url(r'^nexus/control/make_default_metapage/(\d+)/$', 
            dialogs.make_default_metapage),
        url(r'^nexus/control/remove_page_translation/(\d+)/$', 
            dialogs.remove_page_translation),
        url(r'^nexus/control/menu_listing/(\d+)/$', dialogs.menu_listing),
        url(r'^nexus/control/add_menuitem/(\d+)/(\d+)/(.*)/$', 
            dialogs.add_menuitem),

        # site dialogs
        url(r'^nexus/control/missing_site_languages/(\d+)/$', 
            dialogs.missing_site_languages),
        url(r'^nexus/control/site_languages/(\d+)/$', dialogs.site_languages),
        url(r'^nexus/control/all_languages/$', dialogs.all_languages),
        url(r'^nexus/control/add_site_lang/(\d+)/(.*)/$', 
            dialogs.add_site_lang),
        url(r'^nexus/control/edit_site/(\d+)/(.*)/(.*)/(.*)/$', 
            dialogs.edit_site),
        url(r'^nexus/control/add_site/(.*)/(.*)/(.*)/$', dialogs.add_site),

        # menu dialogs
        url(r'^nexus/control/add_menu/(\d+)/(.*)/$', dialogs.add_menu),
        url(r'^nexus/control/add_link_menuitem/(\d+)/(.*)/(.*)/$',
            dialogs.add_link_menuitem),
        url(r'^nexus/control/add_header_menuitem/(\d+)/(.*)/(.*)/$',
            dialogs.add_header_menuitem),
        url(r'^nexus/control/remove_menu_warn/(\d+)/$', 
            dialogs.remove_menu_warn),
        url(r'^nexus/control/remove_menu/(\d+)/$', dialogs.remove_menu),

        # menuitem dialogs
        url(r'^nexus/control/remove_menuitem_translation/(\d+)/$', 
            dialogs.remove_menuitem_translation),
        url(r'^nexus/control/remove_menuitem_warn/(\d+)/$', 
            dialogs.remove_menuitem_warn),
        url(r'^nexus/control/remove_menuitem/(\d+)/$', dialogs.remove_menuitem),
        url(r'^nexus/control/add_menuitem_translation/(\d+)/(.*)/(.*)/$', 
            dialogs.add_menuitem_translation),
        url(r'^nexus/control/rename_menuitem_translation/(\d+)/(.*)/$', 
            dialogs.rename_menuitem_translation),
        url(r'^nexus/control/create_menuitem_translation/(\d+)/(.*)/(.*)/$', 
            dialogs.create_menuitem_translation),

        # tag dialogs
        url(r'^nexus/control/add_tag/(\d+)/(.*)/(.*)/$', dialogs.add_tag),
        url(r'^nexus/control/add_tag_translation/(\d+)/(.*)/(.*)/$', 
            dialogs.add_tag_translation),
        url(r'^nexus/control/remove_tag_translation/(\d+)/$',
            dialogs.remove_tag_translation),
        url(r'^nexus/control/remove_tag/(\d+)/$', dialogs.remove_tag),
    ]

    # -------------------
    # Settings Panel
    urlpatterns += [
        url(r'^nexus/config_panel/$', nexus.config_panel),
    ]

    from yacon.views import config_panel 
    urlpatterns += [
        url(r'^nexus/config/add_language/(.*)/(.*)/$', 
            config_panel.add_language),
    ]

    # -------------------
    # Users Panel
    urlpatterns += [
        url(r'^nexus/users_panel/$', RedirectView.as_view(
            url='/yacon/nexus/users/list_users/')),
    ]

    from yacon.views import users_panel 
    urlpatterns += [
        url(r'^nexus/users/list_users/$', users_panel.list_users),
        url(r'^nexus/users/edit_user/(\d+)/$', users_panel.edit_user),
        url(r'^nexus/users/add_user/$', users_panel.add_user),
        url(r'^nexus/users/user_password/(\d+)/$', users_panel.user_password),
        url(r'^nexus/users/su/(\d+)/$', users_panel.switch_to_user),
    ]

    # -------------------
    # Uploads Panel
    urlpatterns += [
        url(r'^nexus/uploads_panel/$', nexus.uploads_panel),
    ]



if conf.site.examples_enabled:
    urlpatterns += [
        url(r'^(examples/uploads/.+\.html)$', TemplateView.as_view()),
    ]
