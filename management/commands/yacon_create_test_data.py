# -*- coding: latin-1 -*-
#
# yacon_create_test_data.py
# blame ctrudeau chr(64) arsensa.com
#
# Unit tests for Yacon

from django.core.management.base import BaseCommand, CommandError
from django.core import management

from yacon.models.language import Language
from yacon.models.site import Site
from yacon.models.pages import MetaPage, Translation
from yacon.utils import create_page_type, create_block_type

class Command(BaseCommand):
    def handle(self, *args, **options):
        # this management command is used to create test data for yacon

        # if it hasn't been done already, use the yacon_create_defaults script
        # as the basis for our data
        try:
            # get the default site
            site = Site.objects.get(name='Localhost Site')
        except Site.DoesNotExist:
            # default site creation script wasn't run, do it ourselves
            management.call_command('yacon_create_defaults')
            site = Site.objects.get(name='Localhost Site')

        # fetch default language
        english = site.default_language

        # add another language to the Site
        french = Language.factory(name='French', identifier='fr')
        site.alternate_language.add(french)

        # create content hierarchy tree
        articles = site.doc_root.create_child('Articles', 'articles', {\
            french:("L'Article", 'lesarticles')})
        health = articles.create_child('Health', 'health', {\
            french:("La Sante", 'sante')})
        fitness = articles.create_child('Fitness', 'fitness', {\
            french:("De Fitness", 'defitness')})
        money = articles.create_child('Money', 'money', {\
            french:("L'Argent", 'argent')})

        blog = site.doc_root.create_child('Blogs', 'blogs', {\
            french:("Le Blog", 'leblog')})

        # create templates for our content
        pt_article = create_page_type('Article Type', 'examples/article.html' )
        pt_blog = create_page_type('Blog Type', 'examples/blog.html' )

        bt_user = create_block_type('User Content', 'blurb', 
            'yacon.models.content', 'FlatContent')
        bt_poll = create_block_type('Poll Content', 'poll', 
            'yacon.models.content', 'FlatContent')
        bt_blog = create_block_type('Blog Content', 'blog', 
            'yacon.models.content', 'FlatContent')

        # -----------------
        # create some pages
        p = MetaPage.create_translated_page(health, pt_article, [
            Translation(english,
                'Steak is good', 'steak',
                {
                    bt_user:\
                        '<p>Steak should be as good for you as it tastes.</p>',
                    bt_poll:"""
<h3>Poll: Favourite Steak?</h3>
<ul>
<li>T-Bone</li>
<li>Filet Mignon</li>
<li>Porterhouse</li>
</ul>
""",
                }),
            Translation(french,
                'Le steak est bon',
                'lesteak',
                {
                    bt_user:\
                        '<p>Steak devrait être aussi bon pour vous comme ' \
                        + 'il les goûts.</p>',
                    bt_poll:"""
<h3>Poll: Steak Favourite?</h3>
<ul>
<li>Steak T-Bone</li>
<li>Filet Mignon</li>
<li>Chateaubriand</li>
</ul>
""",
                }),
            ]
        )
        health.default_metapage = p
        health.save()

        smoking = MetaPage.create_translated_page(health, pt_article, [
            Translation(english,
                'Smoking is bad', 'smoking',
                {
                    bt_user:'<p>Smoking is bad unless you are a salmon.</p>',
                }),
            Translation(french,
                'Fumer est mauvais', 'fumer',
                {
                    bt_user:\
                    '<p>Fumer est mauvais, sauf si vous êtes un saumo.</p>',
                })
            ])

        # add steak poll blocks to smoking pages
        #english_polls = p.blocks(block_type=bt_poll)
        #smoking.add_block(english_polls[0], english)

        #french_page = p.get_page_translation(french)
        #french_poll = french_page.blocks(block_type=bt_poll)[0]
        #smoking.add_block(french_poll, french)

        # Smoking alias in Fitness
        #page = smoking.create_alias_with_default_language(fitness, 
        #    'smoking_fit')

        # blog pages
        for x in range(1, 4):
            MetaPage.create_page(blog, pt_blog, 'Blog %s' % x, 'blog_%s' % x,
                {
                    bt_user:'<p>Blog entry %s.</p>' % x,
                }
            )
