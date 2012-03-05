var oldhtml = '';

function startEditing() {
    var config = {
        toolbar: [
            { 
                name: 'clipboard', 
                items : ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', 
                    '-', 'Undo', 'Redo' ] 
            },
            { 
                name: 'editing', 
                items : ['Find', 'Replace', '-', 'SelectAll'] 
            },
            { 
                name: 'basicstyles', 
                items : ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 
                    'Superscript', '-', 'RemoveFormat' ]
            },
            { 
                name: 'paragraph', 
                items : ['NumberedList', 'BulletedList', '-', 'Outdent', 
                    'Indent', '-', 'Blockquote', '-', 'JustifyLeft', 
                    'JustifyCenter', 'JustifyRight', 'JustifyBlock']
            },
            { 
                name: 'links', 
                items : ['Link', 'Unlink', 'Anchor']
            },
            { 
                name: 'insert', 
                items : ['Image', 'Table', 'HorizontalRule', 'Smiley', 
                    'SpecialChar']
            },
            { 
                name: 'styles', 
                items : ['Styles', 'Format', 'Font', 'FontSize']
            },
            { 
                name: 'colors', 
                items : ['TextColor', 'BGColor']
            },
            { 
                name: 'tools', 
                items : ['ShowBlocks']
            }
        ]
    };

    old_html = $('.yacon_editable_content').html();
    $('.yacon_editable_content').ckeditor(config);
    $('.yacon_editable_edit').hide();
    $('.yacon_editable_done').show();
    $('.yacon_editable_cancel').show();
}

function stopEditing() {
    $('.yacon_editable_edit').show();
    $('.yacon_editable_done').hide();
    $('.yacon_editable_cancel').hide();
    var editor = $('.yacon_editable_content').ckeditorGet();
    editor.destroy();
}

function cancelEditing() {
    $('.yacon_editable_edit').show();
    $('.yacon_editable_done').hide();
    $('.yacon_editable_cancel').hide();
    var editor = $('.yacon_editable_content').ckeditorGet();
    editor.destroy();
    $('.yacon_editable_content').html(old_html);
}

$(document).ready(function() {
    $('.yacon_editable_done').hide();
    $('.yacon_editable_cancel').hide();
});
