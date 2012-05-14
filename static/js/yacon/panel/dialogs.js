function load_folder_dialogs() {
    // *** Folder Toolbar Dialogs
    create_dialog_using_tree('#remove_folder_dialog', 'Remove Folder', 'Remove',
        function() { // url generator
            var node_id = active_node_id();
            return "/yacon/nexus/remove_folder/" + node_id + "/";
        },
        function(data) { // on success of ajax call
            refresh_tree();
        },
        function() { // on completion of ajax call
            $('#remove_folder_dialog').dialog('close');
        }
    );
    create_dialog_using_tree('#add_folder_dialog', 'Add Folder', 'Add',
        function() { // url generator
            var node_id = active_node_id();
            var title = $('#add_folder_form input#add_folder_title').val();
            var slug = $('#add_folder_form input#add_folder_slug').val();
            return "/yacon/nexus/add_folder/" + node_id + "/" + title + "/"
                + slug + "/";
        },
        function(data) { // on success of ajax call
            if( data['error'] == null ) {
                select_me = data['key'];
                refresh_tree();
            }
            else {
                // something was wrong with our slug, show the user
                alert(data['error']);
            }
        },
        function() { // on completion of ajax call
            $('#add_folder_dialog').dialog('close');
        }
    );
    create_dialog_using_tree('#add_page_dialog', 'Add Page', 'Add',
        function() { // url generator
            var node_id = active_node_id();
            var pagetype = $('#add_page_form #add_page_pagetype').val();
            var title = $('#add_page_form input#add_page_title').val();
            var slug = $('#add_page_form input#add_page_slug').val();
            return "/yacon/nexus/add_page/" + node_id + "/" + pagetype + "/" 
                + title + "/" + slug + "/";
        },
        function(data) { // on success of ajax call
            if( data['error'] == null ) {
                select_me = data['key'];
                refresh_tree();
            }
            else {
                // something was wrong with our slug, show the user
                alert(data['error']);
            }
        },
        function() { // on completion of ajax call
            $('#add_page_dialog').dialog('close');
        }
    );
    $('#add_page_dialog').bind('dialogopen.yacon', function(event, ui) {
        // ajax load the page type listing when we pop the dialog
        $.ajax({
            url: "/yacon/nexus/page_types/",
            dataType: "json",
            success: function(data) {
                // remove old sites, replace with what server sent
                repopulate_select('#add_page_pagetype', data);
            }
        });
    });
    create_dialog_using_tree('#add_path_dialog', 'Add Translation', 'Add',
        function() { // url generator
            var node_id = active_node_id();
            var lang = $('#add_path_form #add_path_lang').val();
            var name = $('#add_path_form input#add_path_name').val();
            var slug = $('#add_path_form input#add_path_slug').val();
            return "/yacon/nexus/add_path/" + node_id + "/" + lang 
                + "/" + name + "/" + slug + "/";
        },
        function(data) { // on success of ajax call
            if( data['error'] == null ) {
                select_me = data['key'];
                refresh_tree();
            }
            else {
                // something was wrong with our slug, show the user
                alert(data['error']);
            }
        },
        function() { // on completion of ajax call
            $('#add_path_dialog').dialog('close');
        }
    );
    $('#add_path_dialog').bind('dialogopen.yacon', function(event, ui) {
        // ajax load the language listing when we pop the dialog
        var node_id = active_node_id();
        $.ajax({
            url: "/yacon/nexus/missing_node_translations/" + node_id + "/",
            dataType: "json",
            success: function(data) {
                // remove old translations, replace with what server sent
                repopulate_select('#add_path_lang', data);
            }
        });
    });
}

function load_metapage_dialogs() {
    create_dialog_using_tree('#remove_page_dialog', 'Remove MetaPage', 'Remove',
        function() { // url generator
            var node_id = active_node_id();
            return "/yacon/nexus/remove_page/" + node_id + "/";
        },
        function(data) { // on success of ajax call
            refresh_tree();
        },
        function() { // on completion of ajax call
            $('#remove_page_dialog').dialog('close');
        }
    );

    create_dialog_using_tree('#add_translation_dialog', 'Add Translation', 
        'Add', function() { // url generator
            var node_id = active_node_id();
            var lang = $('#add_translation_form #add_translation_lang').val();
            var title = 
                $('#add_translation_form input#add_translation_title').val();
            var slug = 
                $('#add_translation_form input#add_translation_slug').val();
            return "/yacon/nexus/add_translation/" + node_id + "/" + lang 
                + "/" + title + "/" + slug + "/";
        },
        function(data) { // on success of ajax call
            if( data['error'] == null ) {
                select_me = data['key'];
                refresh_tree();
            }
            else {
                // something was wrong with our slug, show the user
                alert(data['error']);
            }
        },
        function() { // on completion of ajax call
            $('#add_translation_dialog').dialog('close');
        }
    );
    $('#add_translation_dialog').bind('dialogopen.yacon', function(event, ui) {
        // ajax load the language listing when we pop the dialog
        var node_id = active_node_id();
        $.ajax({
            url: "/yacon/nexus/missing_metapage_translations/" + node_id + "/",
            dataType: "json",
            success: function(data) {
                // remove old translations, replace with what server sent
                repopulate_select('#add_translation_lang', data);
            }
        });
    });
}

function load_inline_dialogs() {
    // *** Node Dialogs
    create_dialog_using_tree('#remove_path_dialog', 'Remove Path', 'Remove',
        function() { // url generator
            return "/yacon/nexus/remove_path/" + remove_path_translation_id 
                + "/";
        },
        function(data) { // on success of ajax call
            refresh_tree();
        },
        function() { // on completion of ajax call
            $('#remove_path_dialog').dialog('close');
        }
    );
    create_dialog_using_tree('#edit_path_dialog', 'Edit Path', 'Save',
        function() { // url generator
            var slug = $('#edit_path_form input#edit_path_slug').val();
            var name = $('#edit_path_form input#edit_path_name').val();
            return "/yacon/nexus/edit_path/" + edit_translation_id + "/" 
                + name + "/" + slug + "/";
        },
        function(data) { // on success of ajax call
            refresh_tree();
        },
        function() { // on completion of ajax call
            $('#edit_path_dialog').dialog('close');
        }
    );
}

function load_site_dialogs() {
    create_dialog('#add_site_lang_dialog', 'Add Language', 'Add',
        function() { // url generator
            var site_id = $('#site_select').val();
            var lang = $('#add_site_lang_form #add_site_lang_lang').val();
            return "/yacon/nexus/add_site_lang/" + site_id + "/" + lang + "/";
        },
        function(data) { // on success of ajax call
                refresh_tree();
        },
        function() { // on completion of ajax call
            $('#add_site_lang_dialog').dialog('close');
        }
    );
    $('#add_site_lang_dialog').bind('dialogopen.yacon', function(event, ui) {
        // ajax load the language listing when we pop the dialog
        var site_id = $('#site_select').val();
        $.ajax({
            url: "/yacon/nexus/missing_site_languages/" + site_id + "/",
            dataType: "json",
            success: function(data) {
                // remove old languages, replace with what server sent
                repopulate_select('#add_site_lang_lang', data);
            }
        });
    });
    create_dialog('#edit_site_dialog', 'Edit Site Settings', 'Save',
        function() { // url generator
            var site_id = $('#site_select').val();
            var name = $('#edit_site_form #edit_site_name').val();
            var domain = $('#edit_site_form #edit_site_domain').val();
            var lang = $('#edit_site_form #edit_site_lang').val();
            return "/yacon/nexus/edit_site/" + site_id + "/" + name + "/"
                + domain + "/" + lang + "/";
        },
        function(data) { // on success of ajax call
            if( data['error'] == null ) {
                refresh_tree();
            }
            else {
                // something was wrong with our parms, show the user
                alert(data['error']);
            }
        },
        function() { // on completion of ajax call
            $('#edit_site_dialog').dialog('close');
        }
    );
    $('#edit_site_dialog').bind('dialogopen.yacon', function(event, ui) {
        // ajax load the language listing when we pop the dialog
        var site_id = $('#site_select').val();
        $.ajax({
            url: "/yacon/nexus/site_languages/" + site_id + "/",
            dataType: "json",
            success: function(data) {
                // remove old languages, replace with what server sent
                repopulate_select('#edit_site_lang', data);
            }
        });
    });
    create_dialog('#add_new_site_dialog', 'Add Site', 'Add',
        function() { // url generator
            var name = $('#add_new_site_form #add_new_site_name').val();
            var domain = $('#add_new_site_form #add_new_site_domain').val();
            var lang = $('#add_new_site_form #add_new_site_lang').val();
            return "/yacon/nexus/add_site/" + name + "/" + domain + "/" 
                + lang + "/";
        },
        function(data) { // on success of ajax call
            if( data['error'] == null ) {
                // re-load list of sites
                $.ajax({
                    url: "/yacon/nexus/get_sites/",
                    dataType: "json",
                    success: function(data) {
                        repopulate_select('#site_select', data);
                        // add site actions
                        $('#site_select').append('<option value="nop">' + 
                            '----------</option>');
                        $('#site_select').append('<option value="add">Add '
                            + 'Site' + '</option>');

                        $('#site_select').selectbox('destroy');
                        $('#site_select').selectbox();
                    }
                });
                refresh_tree();
            }
            else {
                // something was wrong with our parms, show the user
                alert(data['error']);
            }
        },
        function() { // on completion of ajax call
            $('#add_new_site_dialog').dialog('close');
        }
    );
    $('#add_new_site_dialog').bind('dialogopen.yacon', function(event, ui) {
        // ajax load the language listing when we pop the dialog
        $.ajax({
            url: "/yacon/nexus/all_languages/",
            dataType: "json",
            success: function(data) {
                // remove old languages, replace with what server sent
                repopulate_select('#add_new_site_lang', data);
            }
        });
    });
    $('#add_new_site_dialog').bind('dialogclose.yacon', function(event, ui) {
        $('#site_select').val(previously_selected_site);
        $('#site_select').selectbox('refresh');
    });
}

function load_dialogs() {
    load_folder_dialogs();
    load_metapage_dialogs();
    load_inline_dialogs();
    load_site_dialogs();
}
