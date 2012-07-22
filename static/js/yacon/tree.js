// =======================================================
// Tree Helper Functions

function create_tree(activate, init_url, lazyread) {
    // if you get here then user selected a site, load the tree
    $("#tree").dynatree({
        onActivate: function(node) {
            activate(node);
        },
        onPostInit: function(isReloading, isError) {
            // check if the "select_me" variable is set, if so choose that
            // node
            if( select_me != null ) {
                choose_item(select_me);
                select_me = null;
            }
            // check if there is an active node
            node = this.getActiveNode();
            if( node == null ) {
                // no active node, set it to our root; tree has invisible
                // root whose second child is our root
                this.getRoot().getChildren()[1].activate()
            }
            else {
                // tree has active node, activate event event doesn't
                // trigger on a reload, our dynamic content is loaded via
                // activate, so force the activation after initialization
                this.reactivate();
            }
        },
        persist: true,
        initAjax: {
            url: init_url(),
            data: {},  // must include this or it barfs
            addExpandedKeyList: true,
        },
        onLazyRead: function(node) {
            lazyread(node);
        }
    });
}

function active_node() {
    var tree = $('#tree').dynatree("getTree");
    var node = tree.getActiveNode();
    return node;
}

function active_node_id() {
    var tree = $('#tree').dynatree("getTree");
    var node = tree.getActiveNode();
    if( node == null )
        return node;

    // load contents of node
    var pieces = node.data.key.split(":");
    return pieces[1];
}

function refresh_tree() {
    var tree = $('#tree').dynatree("getTree");
    tree.reload();
    return tree
}

// global var for synch selection after reload
var select_me = null;

function choose_item(key) {
    var tree = $('#tree').dynatree("getTree");
    var node = tree.getNodeByKey(key);

    if( node != null ) {
        node.activate();
    }
}
