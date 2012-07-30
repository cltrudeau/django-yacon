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
        $("div#node_container").load('/yacon/nexus/uploads/root_control/' 
            + file_type + '/');
    }
    else {
        $("div#node_container").load('/yacon/nexus/uploads/folder_info/' 
            + node.data.key + '/');
    }
}


function lazy_read(node) {
    node.appendAjax({
        url:"/yacon/nexus/uploads/sub_tree/",
        data: {
            "key":node.data.key
        }
    });
}


function init_ajax_url() {
    return '/yacon/nexus/uploads/tree_top/';
}
