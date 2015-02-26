# YACon

yacon: a sweet tasting root plant grown in the Andes
YACon: Yet Another CONtent management system

YACon was created for a client that had particular needs for a CMS that
weren't easily addressed with existing software at the time.  It is a little
different from a traditional CMS in that it forgoes any layout management,
with the intent being that YACon is a developer's toolkit for creating sites
which can have users that create content.  

Some of the features:

- user file management
    - each user gets their own sub-directory for image uploads
- user avatars
- built-in WYSIWYG editing within a django templated page
- HTML sanitizing of user content
- block level content management
    - multiple blocks on a page
    - blocks can show up across pages
- AJAX based admin tools for managing the pages and blocks
- multi-lingual support
- multi-site support

# Dependencies 

YACon depends a great deal on different 3rd-party libraries.  Some of them are
included in the repo (see 
[3rdparty](https://github.com/cltrudeau/django-yacon/3rdparty)
) in full for reference and have the pieces
that were required copied into the static deployment directory.  This was done
to make it fairly easy to deploy YACon.

There are also a limited number of django libraries that are required.  See
the 
[requirements.txt](https://github.com/cltrudeau/django-yacon/requirements.txt)
file for a list.

In addition to the above, the following dependencies are accessed via CDN:

- jquery-1.7.2
- jquery-ui-1.8.19
