function setup() {
    create_tree(activate, init_ajax_url, lazy_read);
}

function activate(node) {
    hide_all_toolbars();

    // load contents of node
    var pieces = node.data.key.split(":");
    var node_type = pieces[0];
    var node_id = pieces[1];

    $("div#node_container").load('/yacon/nexus/uploads/' + node_type 
            + '_info/' + node_id + "/");
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
