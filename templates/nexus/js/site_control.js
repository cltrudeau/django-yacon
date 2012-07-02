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
            create_tree()
        }
    });

    // load list of sites
    $.ajax({
        url: "/yacon/nexus/get_sites/",
        dataType: "json",
        success: function(data) {
            // remove old sites, replace with what server sent
            repopulate_select('#site_select', data);

            {% if not settings.YACON_DISABLE_ADD_SITE %}
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
