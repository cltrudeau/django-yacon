CKEDITOR.editorConfig = function(config)
{
    config.toolbar = [
        {   name: 'clipboard', 
            items : ['Cut', 'Copy', 'Paste', 'PasteText', '-', 'Undo', 'Redo' ] 
        },
        {   name: 'editing', 
            items : ['Find', 'Replace', '-', 'SelectAll'] 
        },
        {   name: 'basicstyles', 
            items : ['Bold', 'Italic', 'Underline', 'Strike', 
                'Subscript', 'Superscript', '-', 'RemoveFormat' ]
        },
        {   name: 'paragraph', 
            items : ['NumberedList', 'BulletedList', '-', 'Outdent', 
                'Indent', '-', 'Blockquote', '-', 'JustifyLeft', 
                'JustifyCenter', 'JustifyRight', 'JustifyBlock']
        },
        {   name: 'links', 
            items : ['Link', 'Unlink', 'Anchor']
        },
        {   name: 'insert', 
            items : ['Image', 'Table', 'HorizontalRule', 'Smiley', 
                'SpecialChar']
        },
        {   name: 'styles', 
            items : ['Format', 'Font', 'FontSize']
        },
        {   name: 'colors', 
            items : ['TextColor', 'BGColor']
        },
        {   name: 'tools', 
            items : ['ShowBlocks']
        }
    ];
    config.contentsCss = '/static/css/article.css';
    config.skin = 'v2';
};

CKEDITOR.on('dialogDefinition', function(event) {
    var name = event.data.name;
    var def = event.data.definition;

    if( name == 'link' ) {
        def.removeContents('target');
        def.removeContents('advanced');

        var info = def.getContents('info');
        info.remove('linkType');
        info.remove('protocol');
    }
    else if( name == 'image' ) {
        def.removeContents('Link');
        def.removeContents('advanced');

        var info = def.getContents('info');
        info.remove('txtAlt');
    }
});
