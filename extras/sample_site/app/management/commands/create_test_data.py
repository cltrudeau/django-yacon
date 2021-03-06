# vim: set fileencoding=utf-8 :
#
# create_test_data.py
#
# sample_site page structures for yacon
import random

from django.db import transaction
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from yacon.models.common import (Language, NodePermissionTypes,
    PagePermissionTypes)
from yacon.models.site import Site
from yacon.models.pages import MetaPage, Translation, Tag
from yacon.models.hierarchy import Menu
from yacon.helpers import (create_page_type, create_dynamic_page_type, 
    create_block_type)

# =============================================================================

lorem = ['lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do ',
'eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim ',
'veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ',
'ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate ',
'velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint ',
'occaecat cupidatat non proident, sunt in culpa qui officia deserunt ',
'mollit anim id est laborum ']


HOME_TEXT = \
"""
<h1>Yacon Sample Site</h1>
<p>
YACon was created for a client that had particular needs for a CMS that
weren't easily addressed with existing software at the time.  It is a little
different from a traditional CMS in that it forgoes any layout management,
with the intent being that YACon is a developer's toolkit for creating sites
which can have users that create content.  
</p>

<p>
Some of the features:
</p>

<ul>
    <li>user file management</li>
    <ul>
        <li>each user gets their own sub-directory for image uploads</li>
    </ul>
    <li>user avatars</li>
    <li>built-in WYSIWYG editing within a django templated page</li>
    <li>HTML sanitizing of user content</li>
    <li>block level content management</li>
    <ul>
        <li>multiple blocks on a page</li>
        <li>blocks can show up across pages</li>
    </ul>
    <li>AJAX based admin tools for managing the pages and blocks</li>
    <li>
        <a href="/main/multilingual/">multi-lingual support</a>
    </li>
    <li>multi-site support</li>
</ul>
"""


MULTILINGUAL_EN = \
"""
<p>
Yacon supports translations of both slugs and pages.  A single MetaPage object
can be reached by multiple slugs with the value of the slug determining which
translated Page to show.  This grouping allows for easy management of the
translated versions of a page.

</p>
<p>

<ul>
    <li><a href="/primo/plurilingue/">This page in Italian</a></li>
</ul>

</p>
"""


MULTILINGUAL_IT = \
"""
<p>
Yacon supporta traduzioni di entrambe le slug e le pagine. Un singolo oggetto
MetaPage può essere raggiunto da più spezzoni con il valore del slug
determinare che tradotto Pagina mostrare. Questo raggruppamento permette una
facile gestione del versioni tradotte di una pagina.
</p>
<p>
Se stai rabbrividendo al italiana, le mie scuse, tradotto da Google.
</p>
<p>

<ul>
    <li><a href="/main/multilingual/">Questa pagina in inglese</a></li>
</ul>

</p>
"""


def random_paragraphs(html=True):
    result = []
    for x in range(0, random.randint(3, 10)):
        last_line = random.randint(0, 6)
        if html:
            result.append('<p>')
        first = True
        for y in range(3, random.randint(6, 10)):
            try:
                line = lorem[last_line]
                last_line += 1
            except IndexError:
                line = lorem[0]
                last_line = 0

            if first:
                line = line.capitalize()
                first = False
            result.append('   ' + line)

        if html:
            result.append('</p>')
        else:
            result.append('\n')
            result.append('\n')

    return ''.join(result)

# =============================================================================

class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        name='Yacon Sample Site'
        domain='localhost:8000'

        english = Language.factory(name='English', identifier='en')
        italian = Language.factory(name='Italian', identifier='it')
        site = Site.create_site(name, domain, languages=[english, italian])

        # create the home page
        bt = create_block_type('Home Content', 'home')
        pt_home = create_page_type('Home Type', 'content/home.html', [bt])
        mp = MetaPage.create_page(site.doc_root, pt_home, 'Home', 'home', 
            {bt:HOME_TEXT})
        mp.make_default_for_node()

        # main hierarchy
        main = site.doc_root.create_child('Main', 'main', 
            {italian:('Primo', 'primo')})
        news = main.create_child('News', 'news')

        private = site.doc_root.create_child('Private', 'private',
            permission=NodePermissionTypes.LOGIN)

        # create templates for our content
        pt_news_listing = create_dynamic_page_type('News Listing Type', 
            'app.views.news_listing' )

        bt_news = create_block_type('News Content', 'news')
        pt_news = create_page_type('News Type', 'content/news.html', [bt_news])

        bt_general = create_block_type('General Content', 'general')
        pt_general = create_page_type('General Type', 'content/general.html',
            [bt_general])

        # -----------------
        # create some pages

        translations = [
            Translation(english, 'Multi-Lingual', 'multilingual', 
                { bt_general:MULTILINGUAL_EN }),
            Translation(italian, 'Plurilingue', 'plurilingue',
                { bt_general:MULTILINGUAL_IT }),
        ]
        mp = MetaPage.create_translated_page(main, pt_general, translations)
        tag = Tag.factory(site, {english:'translated', italian:'tradurre'})
        mp.tags.add(tag)
        stuff_tag = Tag.factory(site, {english:'stuff'})
        mp.tags.add(stuff_tag)
        tag = Tag.factory(site, {italian:'solo'})  # tag w/o default lang
        mp.tags.add(tag)

        menu = Menu.objects.create(name='Menu', site=site)
        mp = MetaPage.create_page(main, pt_general, 'About', 'about',
            { bt_general:'This is the about page' })
        tag = Tag.factory(site, {english:'about'})
        mp.tags.add(tag)
        mp.tags.add(stuff_tag)

        menu.create_child(mp, translations={ english:'About' })
        menu.create_child(translations={ english:'Not a link' })
        menu.create_child(link='http://cnn.com', translations={ 
            english:'External Link' })
        menu.create_child(link='http://cnn.com', translations={ 
            english:'Only shows on login' }, requires_login=True)
        menu.create_child(link='http://cnn.com', translations={ 
            english:'Only shows for admin' }, requires_admin=True)

        mp = MetaPage.create_page(main, pt_general, 'Contact', 'contact',
            { bt_general:'This is the contact page' })
        menu.create_child(mp, translations={ english:'Contact' })

        MetaPage.create_page(main, pt_news_listing, 'News', 
            'news_listing', {})

        # create random news
        for x in range(1, 16):
            title = 'News %s' % x
            MetaPage.create_page(news, pt_news, title, slugify(title),
                { bt_news:random_paragraphs() })

        # create permission test pages
        MetaPage.create_page(private, pt_general, 'Owner only', 'owner-only',
            { bt_general:'Only the owner or superusers should see this' },
            owner=User.objects.get(username='user1'),
            permission=PagePermissionTypes.OWNER)
        MetaPage.create_page(private, pt_general, 'Login required', 'login-req',
            { bt_general:'Anyone with a login should see this' },
            permission=PagePermissionTypes.LOGIN)
        MetaPage.create_page(private, pt_general, 'Inherit', 'inherit',
            { bt_general:'LOGIN perm inherited from Node' })
