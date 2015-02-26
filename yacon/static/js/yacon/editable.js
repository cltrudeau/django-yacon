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

function page_last_updated(page_set) {
    for(var i=0; i < page_set.length; i++) {
        var id = '#page_updated_' + page_set[i][0];
        $(id).each(function() {
            $(this).html(page_set[i][1]);
        });
    }
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
        if( typeof edit_preconditions == 'function' ) {
            edit_preconditions();
        }
        var div = $(this).parent();
        buttons_edit_mode(div, '.yacon_editable');
        var config = get_ckeditor_config(div);

        old_html[div[0].id] = div.children('.yacon_editable_content').html();
        div.children('.yacon_editable_content').ckeditor(config);
        if( typeof edit_postconditions == 'function' ) {
            edit_postconditions();
        }
    });

    // register click handler for all done buttons
    $('.yacon_editable_done').click(function(event) {
        if( typeof done_preconditions == 'function' ) {
            done_preconditions();
        }
        var div = $(this).parent();
        var block_id = div.attr('id');
        var csrf = div.children('.yacon_ajax_csrf').html();
        var editor = div.children('.yacon_editable_content').ckeditorGet();
        $.ajax({
            url:'/yacon/replace_block/',
            success: function(data) {
                if(data == null || data['success'] != true ) {
                    div.children('.yacon_ajax_error').html('<p>An error ' 
                        + 'occurred submitting, please try again.</p>');

                } 
                else {
                    buttons_save_mode(div, '.yacon_editable');
                    div.children('.yacon_ajax_error').hide();
                    page_last_updated(data['last_updated_list']);
                    editor.destroy();

                    if( typeof done_postconditions == 'function' ) {
                        done_postconditions();
                    }
                }
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
        if( typeof cancel_preconditions == 'function' ) {
            cancel_preconditions();
        }
        var div = $(this).parent();
        buttons_save_mode(div, '.yacon_editable');
        div.children('.yacon_ajax_error').hide();
        var editor = div.children('.yacon_editable_content').ckeditorGet();
        editor.destroy();
        div.children('.yacon_editable_content').html(old_html[div[0].id]);
        if( typeof cancel_postconditions == 'function' ) {
            cancel_postconditions();
        }
    });

    // ======================================================================
    // Title Edit Tools

    $('.yacon_title_editable_edit').click(function(event) {
        // hide buttons and store existing content
        var div = $(this).parent();
        buttons_edit_mode(div, '.yacon_title_editable');
        old_html[div[0].id] = div.children('.yacon_editable_content').html();

        // replace existing content with a form for editing
        div.children('.yacon_editable_content').html(
            '<input type="text" name="title_edit" maxlength="50" value="' 
            + old_html[div[0].id].replace(/^\s+|\s+$/g, '') + '">'
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
            success: function(data) {
                if(data == null || data['success'] != true ) {
                    div.children('.yacon_ajax_error').html('<p>An error ' 
                        + 'occurred submitting, please try again.</p>');

                } 
                else {
                    var page_set = [[data['page_id'], data['last_updated']]];
                    page_last_updated(page_set);

                    buttons_save_mode(div, '.yacon_title_editable');
                    div.children('.yacon_editable_content').html(content);
                    div.children('.yacon_ajax_error').hide();
                }
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
        div.children('.yacon_editable_content').html(old_html[div[0].id]);
    });

});
