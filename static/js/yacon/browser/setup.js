function setup() {
    load_toolbars();
    load_dialogs();
    create_tree(activate, init_ajax_url, lazy_read);
}

function activate(node) {
    hide_all_toolbars();

    // load contents of node
    var pieces = node.data.key.split(":");
    var file_type = pieces[0];
    var path = pieces[1];

    if( file_type == 'system') {
        $("div#node_container").load('/yacon/browser/root_control/' + path 
            + '/');
    }
    else {
        $("div#node_container").load('/yacon/browser/show_folder/?node=' 
            + node.data.key);
    }
}


function lazy_read(node) {
    node.appendAjax({
        url:"/yacon/browser/sub_tree/",
        data: {
            "key":node.data.key
        }
    });
}


function init_ajax_url() {
    return '/yacon/browser/tree_top/';
}
