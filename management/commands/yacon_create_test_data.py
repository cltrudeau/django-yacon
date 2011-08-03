from django.core.management.base import BaseCommand, CommandError
from django.core import management

from yacon.models.hierarchy import Site
from yacon.models.pages import PageType, BlockType, Page, Block
from yacon.utils import create_page_type, create_page, create_block_type

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

        # add another language to the Site
        site.add_config('language', 'fr')

        # create content hierarchy tree
        articles = site.doc_root.create_child('Articles', 'articles', {\
            'fr':("L'Article", 'lesarticles')})
        health = articles.create_child('Health', 'health', {\
            'fr':("La Sante", 'sante')})
        fitness = articles.create_child('Fitness', 'fitness', {\
            'fr':("De Fitness", 'defitness')})
        money = articles.create_child('Money', 'money', {\
            'fr':("L'Argent", 'argent')})

        blog = site.doc_root.create_child('Blogs', 'blogs', {\
            'fr':("Le Blog", 'leblog')})

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
        p = create_page('Steak is good', 'steak', health, pt_article, [\
            ('<p>Steak should be as good for you as it tastes.</p>', bt_user),
            ("""
<ul>
<li>T-Bone</li>
<li>Filet</li>
<li>Porterhouse</li>
</ul>
""",
                bt_poll),
            ]
        )
        health.default_page = p
        health.save()

        smoking = create_page('Smoking is bad', 'smoking', health, pt_article, 
            [('<p>Smoking is bad unless you are salmon.</p>', bt_user),
                ("""
<ul>
    <li>Regular</li>
    <li>Slim</li>
    <li>Menthol</li>
</ul>
""",
                    bt_poll),
            ]
        )


        # Smoking alias in Fitness
        page = smoking.create_alias(fitness, 'smoking_fit')

        # blog pages
        for x in range(1, 4):
            create_page('blog %s' % x, 'blog_%s' % x, blog, pt_blog, [\
                    ('<p>Blog entry %s</p>' % x, bt_blog),
                ]
            )
