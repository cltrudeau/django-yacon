// global var for tracking what site was selected if we hit "add site"
var previously_selected_site = null;

function site_setup() {
    $('#site_select').focus(function() {
        // before the change event, store what was in the select
        previously_selected_site = $('#site_select').val();
    });

    // setup change action when a new site is picked
    $('#site_select').change(function() {
        var value = $(this).attr('value');
        if( value == 'nop' ) {
            $('#site_select').val(previously_selected_site);
            $('#site_select').selectbox('refresh');
            return;
        }
        if( value == 'add' ) {
            $('#add_new_site_dialog').dialog('open');
            return;
        }

        // check if a tree exists already
        var tree = $('#tree').dynatree("getTree");
        if( tree.hasOwnProperty('$widget') ) {
            var url = init_ajax_url();
            $('#tree').dynatree("option", "initAjax", {"url": url})
            refresh_tree()
        }
        else {
            create_tree(activate, init_ajax_url, lazy_read)
        }
    });

    // load list of sites
    $.ajax({
        url: "/yacon/nexus/control/get_sites/",
        dataType: "json",
        success: function(data) {
            // remove old sites, replace with what server sent
            repopulate_select('#site_select', data);

            {% if not conf.nexus.add_site_disabled %}
                // add site actions
                $('#site_select').append('<option value="nop">' + 
                    '----------</option>');
                $('#site_select').append('<option value="add">Add Site' +
                    '</option>');
            {% endif %}

            // turn widget into jquery style drop down, then force a change
            // event
            $('#site_select').selectbox();
            $('#site_select').change();
        }
    });
}

function activate(node) {
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
        $("div#node_container").load('/yacon/nexus/control/menus_control/');
    }
    else {
        // non-system node, show the corresponding link
        $("div#node_container").load('/yacon/nexus/control/' + node_type 
            + '_info/' + node_id + "/");
    }
}


function lazy_read(node) {
    node.appendAjax({
        url:"/yacon/nexus/control/sub_tree/",
        data: {
            "key":node.data.key
        }
    });
}


function init_ajax_url() {
    // can't just hardcode the url as it is dependent on the value of the
    // select box; can't just use a variable inside of the select.change()
    // method as the method doesn't get called in certain reload situations
    // (e.g. undo-close tab in FF)
    value = $('#site_select').attr('value');
    if( value == null || value == "nop" || value == "add" ) {
        // select is set to strange item, return default site
        return '/yacon/nexus/control/tree_top_default_site/';
    }

    // select is set to a site, return that url
    return '/yacon/nexus/control/tree_top/' + value + "/";
}
