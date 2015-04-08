# vim: set fileencoding=utf-8 :
#
# create_test_data.py
#
# sample_site page structures for yacon
import random

from django.db import transaction
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from yacon.models.common import Language
from yacon.models.site import Site
from yacon.models.pages import MetaPage
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
        domain='yaconsamplesite.com:8000'

        english = Language.factory(name='English', identifier='en')
        site = Site.create_site(name, domain, languages=[english, ])

        # create the home page
        home_text = \
"""
<h1>Yacon Sample Site</h1>
<p>
Lorem ipsum dolor sit amet, consectetur 
adipisicing elit, sed do eiusmod tempor 
incididunt ut labore et dolore magna 
aliqua. Ut enim ad minim veniam, quis 
nostrud exercitation ullamco laboris 
nisi ut aliquip ex ea commodo consequat. 
Duis aute irure dolor in reprehenderit 
</p>
"""
        bt = create_block_type('Home Content', 'home')
        pt_home = create_page_type('Home Type', 'content/home.html', [bt])
        mp = MetaPage.create_page(site.doc_root, pt_home, 'Home', 'home', 
            {bt:home_text})
        mp.make_default_for_node()

        # main hierarchy
        main = site.doc_root.create_child('Main', 'main')
        news = main.create_child('News', 'news')

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
        menu = Menu.objects.create(name='Menu', site=site)
        mp = MetaPage.create_page(main, pt_general, 'About', 'about',
            { bt_general:'This is the about page' })
        menu.create_child(mp, { english:'About' })
        mp = MetaPage.create_page(main, pt_general, 'Contact', 'contact',
            { bt_general:'This is the contact page' })
        menu.create_child(mp, { english:'Contact' })

        MetaPage.create_page(main, pt_news_listing, 'News', 
            'news_listing', {})

        # create random news
        for x in range(1, 16):
            title = 'News %s' % x
            MetaPage.create_page(news, pt_news, title, slugify(title),
                { bt_news:random_paragraphs() })