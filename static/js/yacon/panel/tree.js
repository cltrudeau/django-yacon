// =======================================================
// Tree Helper Functions

function create_tree() {
    // if you get here then user selected a site, load the tree
    $("#tree").dynatree({
        onActivate: function(node) {
            hide_all_toolbars();

            // load contents of node
            var pieces = node.data.key.split(":");
            var node_type = pieces[0];
            var node_id = pieces[1];

            if( node_type == 'system' && node_id == 'pages') {
                // system node, show a blank page
                $("div#node_container").html('<p>Click on an item in the ' 
                    + 'tree to the left.</p>');
            }
            else if( node_type == 'system' && node_id == 'menus') {
                // load the menus page
                $("div#node_container").load('/yacon/nexus/menus_control/');
            }
            else {
                // non-system node, show the corresponding link
                $("div#node_container").load('/yacon/nexus/' + node_type 
                    + '_info/' + node_id + "/");
            }
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
            url: init_ajax_url()
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

function init_ajax_url() {
    // can't just hardcode the url as it is dependent on the value of the
    // select box; can't just use a variable inside of the select.change()
    // method as the method doesn't get called in certain reload situations
    // (e.g. undo-close tab in FF)
    value = $('#site_select').attr('value');
    if( value == null || value == "nop" || value == "add" ) {
        // select is set to strange item, return default site
        return '/yacon/nexus/full_tree_default_site/';
    }

    // select is set to a site, return that url
    return '/yacon/nexus/full_tree/' + value + "/";
}
