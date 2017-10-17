from django.test import TestCase

from yacon.models.site import Site
from yacon.models.pages import Page, DoubleAliasException
from yacon.models.hierarchy import Node

from yacon.tests.utils import create_test_site

# ============================================================================
# Page Test Cases
# ============================================================================

class PageTestCase(TestCase):
    def setUp(self):
        # create a site to do testing with
        create_test_site()
        self.site = Site.objects.get(name='Localhost Site')

        # get our languages from the site
        self.english = self.site.get_languages('en')[0]
        self.french = self.site.get_languages('fr')[0]

        pp = self.site.parse_path('/articles/health/')
        self.health = pp.node
        self.assertIsInstance(self.health, Node)

        pp = self.site.parse_path('/articles/health/steak')
        self.steak = pp.page
        self.assertIsInstance(self.steak, Page)
        self.lesteak = pp.page.get_translation(self.french)
        self.assertIsInstance(self.lesteak, Page)

        pp = self.site.parse_path('/articles/health/smoking')
        self.smoking = pp.page
        self.assertIsInstance(self.smoking, Page)

    def test_tree(self):
        # ---------------------------------
        # Test in english

        # test invalid URI
        page = self.site.find_page('/foo/bar')
        self.assertEquals(page, None)

        # test a valid URI without a page slug but with default page
        page = self.site.find_page('/articles/health/')
        self.assertEquals(page, self.steak)
        self.assertEquals(page.metapage_alias, None)
        self.assertEquals(page.language, self.english)

        # test a valid URI without a page slug and without default page
        page = self.site.find_page('/articles/fitness/')
        self.assertEquals(page, None)

        # ---------------------------------
        # Test Multi-lingual
        page = self.site.find_page('/lesarticles/sante/lesteak')
        self.assertEquals(page, self.lesteak)
        self.assertEquals(page.metapage_alias, None)
        self.assertEquals(page.language, self.french)

    def test_aliases(self):
        # create an alias of an alias of the steak article
        aliases = self.health.site.doc_root.create_child('Aliases', 'aliases')
        mp_steak = self.steak.metapage
        mp_steak2 = mp_steak.create_alias(aliases)

        # resolve steak2 and make sure it comes back to steak
        self.assertEquals(mp_steak, mp_steak2.resolve_alias())

        # check whether it can be found
        page = self.site.find_page('/aliases/steak')
        self.assertEquals(page, self.steak)
        self.assertEquals(page.metapage_alias, mp_steak2)

        # ensure double alias disallowed
        with self.assertRaises(DoubleAliasException):
            mp_steak2.create_alias(aliases)
