$(document).ready(function() {
    // hide all "edit", "done" and "cancel" buttons
    $('.yacon_ajax_csrf').hide();
    $('.yacon_editable_edit').hide();
    $('.yacon_editable_done').hide();
    $('.yacon_editable_cancel').hide();
    $('.yacon_title_editable_edit').hide();
    $('.yacon_title_editable_done').hide();
    $('.yacon_title_editable_cancel').hide();

    // add extra handling on form submit
    $('#new_page_form').submit(function() {
        $('.yacon_editable').each(function() {
            // insert a text area into our submit form for each editable block
            var div = $(this);
            var key = div.attr('data-key');
            var editor = div.children('.yacon_editable_content').ckeditorGet();
            var content = escape(editor.getData());
            $('#new_page_form').append(
                '<textarea id="' + key + '" name="' + key + 
                        '" style="display:none;">' +
                    content +
                '</textarea>');
        });

        return True
    });


    // create ckeditors for all editable content
    $('.yacon_editable').each(function() {
        var config = get_ckeditor_config($(this));
        $('.yacon_editable_content').ckeditor(config);
    });
});
