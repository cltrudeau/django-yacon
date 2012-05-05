(function( $ ) {
    var methods = {
        init:function( options ) {
            return this.each(function() {
                $(this).addClass('ct-tabs ui-widget ui-corner-all');
                $(this).children('ul').each(function() {
                    $(this).addClass('ct-tabs-nav ui-helper-reset '
                        + 'ui-helper-clearfix ui-widget-header ui-corner-all')
                    $(this).children('li').addClass(
                       'ui-state-default ui-corner-top');
                });
            });
        },
        select:function( choice ) {
            return this.each(function() {
                var selected = 'ct-tabs-selected ui-state-active';
                $(this).find('li #ct-tabs-selected').each(function(){
                    $(this).removeClass(selected)
                });
                $(this).find('li').eq(choice).addClass(selected);
            });
        }
    };
    $.fn.tabnav = function( method ) {
        if( methods[method] ) {
            return methods[method].apply(this, 
                Array.prototype.slice.call(arguments, 1));
        }
        else if( typeof method === 'object' || !method ) {
            return methods.init.apply(this, arguments );
        }
        else {
            $.error('tab-nav does not support method: ' + method);
        }
    };
})( jQuery );
