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
    $('#edit_path_dialog_warn').load("/yacon/nexus/control/edit_path_warn/" 
        + translation_id + "/");

    $('#edit_path_dialog').dialog('open');
}

// global var for which node path to remove
var remove_path_translation_id = null;

function remove_path(translation_id) {
    remove_path_translation_id = translation_id;
    var dialog = $('#remove_path_dialog');
    dialog.load("/yacon/nexus/control/remove_path_warn/" + translation_id 
        + "/");
    dialog.dialog("open");
}

function remove_page_translation(page_id, title, has_alias) {
    if( has_alias == 'True' ) {
        action = confirm('Translation \"' + title + '" is aliased.  Removing '
            + 'the translation will automatically remove it from any aliases. '
            + 'Are you sure you want to remove it?');
    }
    else {
        action = confirm('Remove translation \"' + title + '"?');
    }

    if( action ) {
        $.ajax({
            url: "/yacon/nexus/control/remove_page_translation/" + page_id 
                + "/",
            dataType: "json",
            success: function(data) {
                refresh_tree();
            }
        });
    }
}

function edit_site(site_id, name, domain) {
    $('#edit_site_form input#edit_site_name').val(name);
    $('#edit_site_form input#edit_site_domain').val(domain);

    $('#edit_site_dialog').dialog('open');
}


function remove_menuitem_translation(menuitem_id, title) {
    action = confirm('Remove translation \"' + title + '"?');
    if( action ) {
        $.ajax({
            url: "/yacon/nexus/control/remove_menuitem_translation/" 
                + menuitem_id + "/",
            dataType: "json",
            success: function(data) {
                refresh_tree();
            }
        });
    }
}

function edit_block(block_id) {
    $.ajax({
        url: "/yacon/fetch_block/" + block_id + "/",
        dataType: "json",
        success: function(data) {
            $('#block_id').html(block_id);
            var textarea = $('#edit_block_dialog textarea')
            textarea.attr('contenteditable', true);
            textarea.html(data);
            CKEDITOR.replace(textarea[0], {
                filebrowserBrowseUrl:'/yacon/ckeditor_browser/',
                filebrowserUploadUrl:'/yacon/ckeditor_browser/?image_only=1',
            });
            $('#edit_block_dialog').dialog('open');
        }
    });
}

function edit_owner(metapage_id) {
    $.ajax({
        url: "/yacon/fetch_owner/" + metapage_id + "/",
        dataType: "json",
        success: function(data) {
            $('#metapage_id').html(metapage_id);
            var select = $('#owners');
            select.html('');
            select.append(
                $('<option>').attr('value', '0').text('')
            );
            $(data['users']).each(function() {
                select.append(
                    $('<option>').attr('value', this[0]).text(this[1])
                );
            });
            select.val(data['selected']);

            $('#edit_owner_dialog').dialog('open');
        }
    });
}

function edit_metapage_perm(metapage_id, perm) {
    $('#metapage_id').html(metapage_id);
    $('#edit_metapage_perm .perms').val(perm);
    $('#edit_metapage_perm').dialog('open');
}

function edit_node_perm(node_id, perm) {
    $('#node_id').html(node_id);
    $('#edit_node_perm .perms').val(perm);
    $('#edit_node_perm').dialog('open');
}
