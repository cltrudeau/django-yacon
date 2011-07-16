from django.core.management.base import BaseCommand, CommandError

from yacon.models.hierarchy import ContentHierarchy
from yacon.models.pages import PageType, BlockSpecifier, Page, Block

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
        article_type = PageType(name='Article Type',
            template='examples/article.html' )
        article_type.save()
        blog_type = PageType(name='Blog Type', template='examples/blog.html' )
        blog_type.save()

        user_cs = BlockSpecifier(name='User Content', key='blurb', 
            mod='yacon.models.content', content_handler='FlatContent')
        user_cs.save()
        poll_cs = BlockSpecifier(name='Poll Content', key='poll', 
            mod='yacon.models.content', content_handler='FlatContent')
        poll_cs.save()
        blog_cs = BlockSpecifier(name='Blog Content', key='blog', 
            mod='yacon.models.content', content_handler='FlatContent')
        blog_cs.save()

        # -----------------
        # create some pages

        # Steak
        s = '<p>Steak should be as good for you as it tastes.</p>'
        con = Block(specifier=user_cs, content=s)
        con.save()
        s = \
"""
<ul>
    <li>Steak</li>
    <li>Steak</li>
    <li>Steak</li>
</ul>
"""
        poll = Block(specifier=poll_cs, content=s)
        poll.save()

        page = Page(title='Steak is good', slug='steak', node=health,
            pagetype=article_type)
        page.save()
        page.blocks.add(con)
        page.blocks.add(poll)

        # Smoking 
        s = '<p>Smoking is bad unless you are salmon.</p>'
        con = Block(specifier=user_cs, content=s)
        con.save()
        s = \
"""
<ul>
    <li>Regular</li>
    <li>Slim</li>
    <li>Menthol</li>
</ul>
"""
        poll = Block(specifier=poll_cs, content=s)
        poll.save()

        page = Page(title='Smoking is bad', slug='smoking', node=health, 
            pagetype=article_type)
        page.save()
        page.blocks.add(con)
        page.blocks.add(poll)

        # Smoking alias in Fitness
        page = Page(title='Smoking is bad', slug='smoking_fit', node=fitness,
            pagetype=article_type)
        page.save()
        page.blocks.add(con)
        page.blocks.add(poll)

        # blog pages
        for x in range(1, 4):
            s = '<p>Blog entry %s</p>' % x
            con = Block(specifier=blog_cs, content=s)
            con.save()

            page = Page(title='blog %s' % x, slug='blog_%s' % x, node=blog,
                pagetype=blog_type)
            page.save()
            page.blocks.add(con)
