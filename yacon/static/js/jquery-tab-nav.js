/* jQuery Tab Nav
 *
 * Copyright 2012 Christopher Trudeau
 * https://github.com/cltrudeau/jquery-tab-nav
 * MIT License
 */

(function( $ ) {
    var SELECTED = 'ct-tabs-selected ui-state-active';
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
                $(this).find('li #ct-tabs-selected').each(function(){
                    $(this).removeClass(SELECTED)
                });
                $(this).find('li').eq(choice).addClass(SELECTED);
            });
        },
        select_by_id:function( choice ) {
            return this.each(function() {
                $(this).find('li #ct-tabs-selected').each(function(){
                    $(this).removeClass(SELECTED)
                });
                $(this).find('li#' + choice).addClass(SELECTED);
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
