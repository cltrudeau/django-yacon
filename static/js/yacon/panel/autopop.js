function load_autopopulate_fields() {
    // *** Add Folder 
    $('#add_folder_slug').bind('change.yacon', function() {
        $(this).data('changed', true);
    });
    $('#add_folder_title').bind('keyup.yacon', function() {
        var e = $('#add_folder_slug');
        if( !e.data('changed') ) {
            e.val(URLify($('#add_folder_title').val(), 50));
        }
    });

    // *** Add Page 
    $('#add_page_slug').bind('change.yacon', function() {
        $(this).data('changed', true);
    });
    $('#add_page_title').bind('keyup.yacon', function() {
        var e = $('#add_page_slug');
        if( !e.data('changed') ) {
            e.val(URLify($('#add_page_title').val(), 50));
        }
    });

    // *** Add Translation 
    $('#add_translation_slug').bind('change.yacon', function() {
        $(this).data('changed', true);
    });
    $('#add_translation_title').bind('keyup.yacon', function() {
        var e = $('#add_translation_slug');
        if( !e.data('changed') ) {
            e.val(URLify($('#add_translation_title').val(), 50));
        }
    });
}
