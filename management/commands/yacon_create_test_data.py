from django.core.management.base import BaseCommand, CommandError

from yacon.models.hierarchy import ContentHierarchy
from yacon.models.pages import PageType, BlockType, Page, Block
from yacon.utils import create_page_type, create_page, create_block_type

class Command(BaseCommand):
    def handle(self, *args, **options):
        # this management command is used to create test data for yacon

        # create content hierarchy tree
        root = ContentHierarchy.get_root()
        articles = root.add_child(name='Articles', slug='articles')
        health = articles.add_child(name='Health', slug='health')
        fitness = articles.add_child(name='Fitness', slug='fitness')
        money = articles.add_child(name='Money', slug='money')

        blog = root.add_child(name='Blogs', slug='blogs')

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
        create_page('Steak is good', 'steak', health, pt_article, [\
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
