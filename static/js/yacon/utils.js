function repopulate_select(selector, data) {
    $(selector).children().remove();
    for( var key in data ){
        if( data.hasOwnProperty(key) ){
            console.debug('adding key: ' + key);
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

function create_dialog(selector, title, ok_label, url_generator, success) {

    // call full with default behaviour for pressing the ok button
    create_dialog_full(selector, title, ok_label, 
        function() {
            var url = url_generator();
            $.ajax({
                url: url,
                success: success,
            });
        });
}

function create_dialog_full(selector, title, ok_label, ok_press) {
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
                    ok_press()
                    $(this).dialog('close');
                    return false;
                }
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

function create_dialog_using_tree(selector, title, ok_label, url_generator, 
        success) {
    // call full with behaviour for items dealing with a selected node in the
    // tree
    create_dialog_full(selector, title, ok_label, 
        function() {
            var node_id = active_node_id();
            if( node_id != null ) {
                var url = url_generator();
                $.ajax({
                    url: url,
                    success: success,
                });
            }
            else {
                $(this).dialog('close');
            }
            return false;
        });
}
