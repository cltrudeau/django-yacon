$(document).ready(function() {
    // hide all "edit", "done" and "cancel" buttons
    $('.yacon_ajax_csrf').hide();
    $('.yacon_editable_edit').hide();
    $('.yacon_editable_done').hide();
    $('.yacon_editable_cancel').hide();
    $('.yacon_title_editable_edit').hide();
    $('.yacon_title_editable_done').hide();
    $('.yacon_title_editable_cancel').hide();

    debugger;

    // create textareas in the form for each block
    $('.yacon_editable').each(function() {
        var key = $(this).attr('data-key');
        $('#new_page_form').append( 
            '<textarea id="' + key + '" name="' + key + '"></textarea>'
        );
    });
    $('#article').hide();
    CKEDITOR.replaceAll();
});
