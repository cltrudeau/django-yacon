// =======================================================
// General Helper Functions

function hide_all_toolbars() {
    $('#folder_toolbar').hide();
    $('#metapage_toolbar').hide();
    $('#add_translation').hide()
    $('#add_path').hide()
}

function repopulate_select(selector, data) {
    $(selector).children().remove();
    for( var key in data ){
        if( data.hasOwnProperty(key) ){
            $(selector).append('<option value="' + key + '">' + data[key] 
                + '</option>');
        }
    }
}

function count_keys(data) {
    num_keys = 0;
    for( var key in data ){
        if( data.hasOwnProperty(key) ){
            num_keys++;
        }
    }
    return num_keys;
}

// =======================================================
// Dialog Creation Function

function create_dialog(selector, title, ok_label, url_generator, success, 
        complete) {
    var height = Math.floor(0.80 * $(window).height());
    var width = Math.floor(0.80 * $(window).width());

    $(selector).dialog({
        autoOpen: false,
        modal: true,
        maxHeight: height,
        height: height,
        maxWidth: width,
        width: width,
        buttons: [
            {
                text:ok_label,
                click: function() {
                    var node_id = active_node_id();
                    if( node_id != null ) {
                        var url = url_generator();
                        $.ajax({
                            url: url,
                            success: success,
                            complete: complete,
                        });
                    }
                    else {
                        $(this).dialog('close');
                    }
                    return false;
                },
            },
            {
                text:"Cancel",
                click:function() {
                    $(this).dialog('close');
                    return false;
                }
            },
        ],
        title: title,
    });
}

// =======================================================
// Inline Action Functions

// global var for which node path to edit
var edit_translation_id = null;

function edit_path(translation_id, lang_code, name, path) {
    edit_translation_id = translation_id;
    var parts = path.split('/');
    var slug = parts.pop();
    if( slug == '' ) 
        slug = parts.pop();

    $('#edit_path_form input#edit_path_lang').val(lang_code);
    $('#edit_path_form input#edit_path_name').val(name);
    $('#edit_path_form input#edit_path_slug').val(slug);
    $('#edit_path_dialog_warn').load("/yacon/nexus/edit_path_warn/" 
        + translation_id + "/");

    $('#edit_path_dialog').dialog('open');
}

// global var for which node path to remove
var remove_path_translation_id = null;

function remove_path(translation_id) {
    remove_path_translation_id = translation_id;
    var dialog = $('#remove_path_dialog');
    dialog.load("/yacon/nexus/remove_path_warn/" + translation_id + "/");
    dialog.dialog("open");
}

function remove_page_translation(page_id, title) {
    action = confirm('Remove translation \"' + title + '"?');
    if( action ) {
        $.ajax({
            url: "/yacon/nexus/remove_page_translation/" + page_id + "/",
            dataType: "json",
            success: function(data) {
                refresh_tree();
            }
        });
    }
}
