jquery-tab-nav
==============

jQuery widget for creating a nav bar that looks like the jquery ui tabs
component.

The jquery-ui-tabs component is great, but it requires everything to be on the
same page in divs or loaded via AJAX.  This component uses the jquery-ui
themeroller stylings and presents an series of tabs directly connected to
links.  The intent is to use the the nav inside of a common header file and
then select the current tab in each page.

Selection of a tab can be done via an index number into the ul, or by id on
the li.

Example usage
-------------

### Select By Index ###

    <div id="navbar">
        <ul>
            <li> <a href="one.html">One</a> </li>
            <li> <a href="two.html">Two</a> </li>
        </ul>
    </div>

    $('#navbar').tabnav();
    $('#navbar').tabnav('select', 0);

### Select By ID ###

    <div id="navbar">
        <ul>
            <li id="one"> <a href="one.html">One</a> </li>
            <li id="two"> <a href="two.html">Two</a> </li>
        </ul>
    </div>

    $('#navbar').tabnav();
    $('#navbar').tabnav('select_by_id', 'two');

See the pages in "examples/" for reference.

License
-------
MIT license, compatible with jquery

Mea Culpa
---------
I've done very little testing on this, across browsers or with
different themes, it is pretty simple and shouldn't be a problem, but given
the state of the web, I'm not holding my breath

TODO
----
* would be nice to auto-select the tab based on the URL
