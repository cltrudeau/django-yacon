var old_html = Array();

$(document).ready(function() {
    // hide all "done" and "cancel" buttons
    $('.yacon_ajax_csrf').hide();
    $('.yacon_editable_done').hide();
    $('.yacon_editable_cancel').hide();

    // register click handler for all edit buttons
    $('.yacon_editable_edit').click(function(event) {
        var div = $(this).parent();
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
        div.children('.yacon_editable_edit').hide();
        div.children('.yacon_editable_done').show();
        div.children('.yacon_editable_cancel').show();
    });

    // register click handler for all done buttons
    $('.yacon_editable_done').click(function(event) {
        var div = $(this).parent();
        var block_id = div.attr('id');
        var csrf = div.children('.yacon_ajax_csrf').html();
        var editor = div.children('.yacon_editable_content').ckeditorGet();
        $.ajax({
            url:'/yacon/ajax_submit/',
            success: function() {
                div.children('.yacon_editable_edit').show();
                div.children('.yacon_editable_done').hide();
                div.children('.yacon_editable_cancel').hide();
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
        div.children('.yacon_editable_edit').show();
        div.children('.yacon_editable_done').hide();
        div.children('.yacon_editable_cancel').hide();
        div.children('.yacon_ajax_error').hide();
        var editor = div.children('.yacon_editable_content').ckeditorGet();
        editor.destroy();
        div.children('.yacon_editable_content').html(old_html[div.id]);
    });
});


