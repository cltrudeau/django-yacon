function load_dialogs() {
    create_dialog('#add_language_dialog', 'Add Language', 'Add',
        function() { // url generator
            var name = $('#add_language_form input#add_language_name').val();
            var identifier = 
                $('#add_language_form input#add_language_identifier').val();
            return "/yacon/nexus/add_language/" + name + "/" + identifier + "/";
        },
        function(data) { // on success of ajax call
            window.location.href = '/yacon/nexus/config/';
        },
        function() { // on completion of ajax call
        }
    );
}
