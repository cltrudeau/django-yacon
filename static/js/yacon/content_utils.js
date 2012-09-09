function get_ckeditor_config(div) {
    var config_file = '/static/js/yacon/ckeditor_config.js';
    if( typeof config_file_overwrite == 'string' ) {
        config_file = config_file_overwrite;
    }
    var config = {
        customConfig: config_file,
        height: div.height(),
        width: div.width(),
        filebrowserBrowseUrl:'/yacon/ckeditor_browser/',
        filebrowserImageBrowseUrl:'/yacon/ckeditor_browser/?image_only=1',
    };
    if( typeof extra_config == 'object') {
        for(var name in extra_config) {
            if( extra_config.hasOwnProperty(name)) {
                config[name] = extra_config[name];
            }
        }
    }

    return config
}
