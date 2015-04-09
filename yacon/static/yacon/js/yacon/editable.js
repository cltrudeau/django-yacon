var old_html = Array();

function buttons_edit_mode(block, name) {
    block.find(name + '_edit').hide();
    block.find(name + '_cancel').show();
    block.find(name + '_done').show();
}

function buttons_save_mode(block, name) {
    block.find(name + '_edit').show();
    block.find(name + '_cancel').hide();
    block.find(name + '_done').hide();
}

function page_last_updated(page_set) {
    for(var i=0; i < page_set.length; i++) {
        var id = '#page_updated_' + page_set[i][0];
        $(id).each(function() {
            $(this).html(page_set[i][1]);
        });
    }
}

function first_editor() {
    return CKEDITOR.instances[Object.keys(CKEDITOR.instances)[0]];
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
        var button = $(this);
        button.append('<span class="spinner">&nbsp;&nbsp;' + 
            '<img height="25" src="/static/yacon/images/uploads/loading.gif">'
            + '</span>');
        var block = $(this).parent().parent();
        old_html[block[0].id] = block.children(
            '.yacon_editable_content').html();
        var to_edit = block.children('.yacon_editable_content');
        to_edit.attr('contenteditable', true);

        CKEDITOR.inline(to_edit[0], {
            startupFocus:true,
            on: {
                instanceReady:function(ev) {
                    buttons_edit_mode(block, '.yacon_editable');
                    button.find('.spinner').remove();
                }
            },
        });
    });

    // register click handler for all done buttons
    $('.yacon_editable_done').click(function(event) {
        var block = $(this).parent().parent();
        var csrf = block.find('.yacon_ajax_csrf').html();
        $.ajax({
            url:'/yacon/replace_block/',
            success: function(data) {
                if(data == null || data['success'] != true ) {
                    block.find('.yacon_ajax_error').html('<p>An error ' 
                        + 'occurred submitting, please try again.</p>');
                } 
                else {
                    block.find('.yacon_ajax_error').hide();
                    page_last_updated(data['last_updated_list']);
                    first_editor().destroy();

                    var to_edit = block.children('.yacon_editable_content');
                    to_edit.attr('contenteditable', false);
                    buttons_save_mode(block, '.yacon_editable');
                }
            },
            error: function() {
                block.find('.yacon_ajax_error').html(
                    '<p>An error occurred submitting, please try again.</p>');
            },
            type:'POST',
            data: {
                'block_id':block[0].id,
                'content':first_editor().getData(),
                'csrfmiddlewaretoken':csrf
            }
        });
    });

    // register click handler for all cancel buttons
    $('.yacon_editable_cancel').click(function(event) {
        var block = $(this).parent().parent();
        buttons_save_mode(block, '.yacon_editable');

        block.find('.yacon_ajax_error').hide();
        first_editor().destroy();

        var to_edit = block.children('.yacon_editable_content');
        to_edit.attr('contenteditable', false);

        block.find('.yacon_editable_content').html(old_html[block[0].id]);
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
