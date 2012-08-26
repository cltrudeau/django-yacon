var old_html = Array();

function buttons_edit_mode(div, name) {
    $(name + '_edit').hide();
    $(name + '_cancel').show();
    $(name + '_done').show();
}
function buttons_save_mode(div, name) {
    $(name + '_edit').show();
    $(name + '_cancel').hide();
    $(name + '_done').hide();
}

$(document).ready(function() {
    // hide all "done" and "cancel" buttons
    $('.yacon_ajax_csrf').hide();
    $('.yacon_editable_done').hide();
    $('.yacon_editable_cancel').hide();
    $('.yacon_title_editable_done').hide();
    $('.yacon_title_editable_cancel').hide();

    // ======================================================================
    // CKEdit Tools

    // register click handler for all edit buttons
    $('.yacon_editable_edit').click(function(event) {
        var div = $(this).parent();
        buttons_edit_mode(div, '.yacon_editable');
        var config = {
            toolbar: [
                {   name: 'clipboard', 
                    items : ['Cut', 'Copy', 'Paste', 'PasteText', 
                        'PasteFromWord', '-', 'Undo', 'Redo' ] 
                },
                {   name: 'editing', 
                    items : ['Find', 'Replace', '-', 'SelectAll'] 
                },
                {   name: 'basicstyles', 
                    items : ['Bold', 'Italic', 'Underline', 'Strike', 
                        'Subscript', 'Superscript', '-', 'RemoveFormat' ]
                },
                {   name: 'paragraph', 
                    items : ['NumberedList', 'BulletedList', '-', 'Outdent', 
                        'Indent', '-', 'Blockquote', '-', 'JustifyLeft', 
                        'JustifyCenter', 'JustifyRight', 'JustifyBlock']
                },
                {   name: 'links', 
                    items : ['Link', 'Unlink', 'Anchor']
                },
                {   name: 'insert', 
                    items : ['Image', 'Table', 'HorizontalRule', 'Smiley', 
                        'SpecialChar']
                },
                {   name: 'styles', 
                    items : ['Styles', 'Format', 'Font', 'FontSize']
                },
                {   name: 'colors', 
                    items : ['TextColor', 'BGColor']
                },
                {   name: 'tools', 
                    items : ['ShowBlocks']
                }
            ]
        };

        old_html[div.id] = div.children('.yacon_editable_content').html();
        div.children('.yacon_editable_content').ckeditor(config);
    });

    // register click handler for all done buttons
    $('.yacon_editable_done').click(function(event) {
        var div = $(this).parent();
        var block_id = div.attr('id');
        var csrf = div.children('.yacon_ajax_csrf').html();
        var editor = div.children('.yacon_editable_content').ckeditorGet();
        $.ajax({
            url:'/yacon/replace_block/',
            success: function() {
                buttons_save_mode(div, '.yacon_editable');
                div.children('.yacon_ajax_error').hide();
                editor.destroy();
            },
            error: function() {
                div.children('.yacon_ajax_error').html(
                    '<p>An error occurred submitting, please try again.</p>');
            },
            type:'POST',
            data: {
                'block_id':block_id,
                'content':editor.getData(),
                'csrfmiddlewaretoken':csrf
            }
        });
    });

    // register click handler for all cancel buttons
    $('.yacon_editable_cancel').click(function(event) {
        var div = $(this).parent();
        buttons_save_mode(div, '.yacon_editable');
        div.children('.yacon_ajax_error').hide();
        var editor = div.children('.yacon_editable_content').ckeditorGet();
        editor.destroy();
        div.children('.yacon_editable_content').html(old_html[div.id]);
    });

    // ======================================================================
    // Title Edit Tools

    $('.yacon_title_editable_edit').click(function(event) {
        // hide buttons and store existing content
        var div = $(this).parent();
        buttons_edit_mode(div, '.yacon_title_editable');
        old_html[div.id] = div.children('.yacon_editable_content').html();

        // replace existing content with a form for editing
        div.children('.yacon_editable_content').html(
            '<input type="text" name="title_edit" maxlength="25" value="' 
            + old_html[div.id].replace(/^\s+|\s+$/g, '') + '">'
        );
    });

    // register click handler for all done buttons
    $('.yacon_title_editable_done').click(function(event) {
        var div = $(this).parent();
        var page_id = div.attr('id');
        var csrf = div.children('.yacon_ajax_csrf').html();

        // get the value and strip it of spaces
        var content = div.find('.yacon_editable_content input').val();
        content = content.replace(/^\s+|\s+$/g, '');
        $.ajax({
            url:'/yacon/replace_title/',
            success: function() {
                buttons_save_mode(div, '.yacon_title_editable');
                div.children('.yacon_editable_content').html(content);
                div.children('.yacon_ajax_error').hide();
            },
            error: function() {
                div.children('.yacon_ajax_error').html(
                    '<p>An error occurred submitting, please try again.</p>');
            },
            type:'POST',
            data: {
                'page_id':page_id,
                'content':content,
                'csrfmiddlewaretoken':csrf
            }
        });
    });

    // register click handler for all cancel buttons
    $('.yacon_title_editable_cancel').click(function(event) {
        var div = $(this).parent();
        buttons_save_mode(div, '.yacon_title_editable');
        div.children('.yacon_ajax_error').hide();
        div.children('.yacon_editable_content').html(old_html[div.id]);
    });

});
