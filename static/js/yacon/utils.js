function repopulate_select(selector, data) {
    $(selector).children().remove();
    for( var key in data ){
        if( data.hasOwnProperty(key) ){
            $(selector).append('<option value="' + key + '">' + data[key]
                + '<option>');
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

function create_dialog(selector, title, ok_label, url_generator, success, 
        complete) {

    // call full with default behaviour for pressing the ok button
    create_dialog_full(selector, title, ok_label, 
        function() {
            var url = url_generator();
            $.ajax({
                url: url,
                success: success,
                complete: complete,
            });
        },
        url_generator, success, complete);
}

function create_dialog_full(selector, title, ok_label, ok_press, url_generator, 
        success, complete) {
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
                click: ok_press,
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
