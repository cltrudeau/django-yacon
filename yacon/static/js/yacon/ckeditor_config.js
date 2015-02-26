CKEDITOR.editorConfig = function(config)
{
    config.toolbar = [
        {   name: 'clipboard', 
            items : ['Cut', 'Copy', 'Paste', 'PasteText', 
                'PasteFromWord', '-', 'Undo', 'Redo' ] 
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
            items : ['Styles', 'Format', 'Font', 'FontSize']
        },
        {   name: 'colors', 
            items : ['TextColor', 'BGColor']
        },
        {   name: 'tools', 
            items : ['ShowBlocks']
        }
    ]
    config.skin = 'v2';
};
