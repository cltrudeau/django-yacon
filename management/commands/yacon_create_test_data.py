# vim: set fileencoding=utf-8 :
#
# yacon_create_test_data.py
# blame ctrudeau chr(64) arsensa.com
#
# Unit tests for Yacon

from django.core.management.base import BaseCommand
from django.core import management

from yacon.models.common import Language
from yacon.models.site import Site
from yacon.models.pages import MetaPage, Translation
from yacon.models.hierarchy import NodeTranslation, Menu
from yacon.models.users import UserProfile
from yacon.helpers import create_page_type, create_block_type

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

        # so we can test what happens if a node is missing a default language,
        # find the english money node translation and remove it
        tx = NodeTranslation.objects.get(node=money, language=english)
        tx.delete()

        # create templates for our content
        pt_article = create_page_type('Article Type', 'examples/article.html' )
        pt_blog = create_page_type('Blog Type', 'examples/blog.html' )

        bt_user = create_block_type('User Content', 'blurb', 
            'yacon.models.content', 'FlatContent')
        bt_poll = create_block_type('Poll Content', 'poll', 
            'yacon.models.content', 'FlatContent')
        bt_blog = create_block_type('Blog Content', 'blog', 
            'yacon.models.content', 'FlatContent')
        create_block_type('Right Now Content', 'right_now', 
            'yacon.models.content', 'DynamicContent', 
            {'module':'yacon.examples.dynamic', 'function':'right_now'})

        # create a couple of menus
        menu1 = Menu.objects.create(name='Menu 1', site=site)

        # -----------------
        # create some pages
        mp = MetaPage.create_translated_page(site.doc_root, pt_article, [
            Translation(english,
                'Home Page', 'homepage',
                {
                    bt_user:('<p>This is a most excellent home page.</p>'),
                    bt_poll:"""
<h3>Poll: Is This Your Favourite Home Page?</h3>
<ul>
<li>Yes</li>
<li>Yes, most definitely</li>
</ul>
""",
                }),
            ]
        )
        mp.make_default_for_node()
        site.doc_root.save()
        menu1.create_child(mp)
        sub_menu = menu1.create_child(None, { english:'Sub Menu1' })
        sm2 = sub_menu.create_child(None, { english:'Sub Menu1.1' })
        sm2.create_child(None, { english:'Sub Menu1.1.1' })

        mp = MetaPage.create_translated_page(health, pt_article, [
            Translation(english,
                'Steak is good', 'steak',
                {
                    bt_user:('<p>Steak should be as good for you as it '
                        'tastes.</p>'),
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
                    bt_user:('<p>Steak devrait être aussi bon pour vous comme '
                        'it les goûts.</p>'),
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
        mp.make_default_for_node()
        health.save()
        sub_menu.create_child(mp)

        # create a page without the default translation
        MetaPage.create_translated_page(health, pt_article, [
            Translation(french,
                'Trans-graisses vous tuer',
                'transgraisses',
                {
                    bt_user: ("<p>Trans-gras ve ta tuer, mais ce n'est pas de "
                        'nos jours?</p>'),
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

        # when creating the smoking pages use the blocks from steak polls
        poll = mp.get_translation(english).blocks.filter(block_type=bt_poll)[0]
        lepoll = mp.get_translation(french).blocks.filter(
            block_type=bt_poll)[0]

        smoking = MetaPage.create_translated_page(health, pt_article, [
            Translation(english,
                'Smoking is bad', 'smoking',
                {
                    bt_user:'<p>Smoking is bad unless you are a salmon.</p>',
                    bt_poll:poll.content,
                }),
            Translation(french,
                'Fumer est mauvais', 'fumer',
                {
                    bt_user:('<p>Fumer est mauvais, sauf si vous êtes un '
                        'saumo.</p>'),
                    bt_poll:lepoll.content,
                })
            ])
        sub_menu.create_child(smoking, {english:'Puffing', french:'Le Puffing'})

        # Smoking alias in Fitness
        smoking.create_alias(fitness)

        # blog pages
        for x in range(1, 40):
            MetaPage.create_page(blog, pt_blog, 'Blog %s' % x, 'blog_%s' % x,
                {
                    bt_blog:'<p>Blog entry %s.</p>' % x,
                }
            )

        # -----------------
        # create a second site
        Site.create_site('Second Site', 'dummyhost', 
            languages=[site.default_language])

        # -----------------
        # create some test users
        UserProfile.create('fflintstone', 'Fred', 'Flintstone', 
            'fred@quarry.com', 'yabbadabbadoo')
        UserProfile.create('brubble', 'Barney', 'Rubble', 
            'barney@quarry.com', 'yabbadabbadoo')

        # create an admin
        profile = UserProfile.create('admin', 'A', 'Admin', 'admin@admin.com', 
            'admin')
        profile.user.is_staff = True
        profile.user.is_superuser = True
        profile.user.save()
