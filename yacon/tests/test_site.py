from django.test import TestCase

from yacon.models.common import Language
from yacon.models.site import Site, ParsedPath
from yacon.models.hierarchy import BadSlug

# ============================================================================
# Site and Hierachy Test Cases
# ============================================================================

class SiteTestCase(TestCase):
    def test_hierarchy(self):
        british = Language.factory(name='GB English', identifier='en-gb')
        french = Language.factory(name='French', identifier='fr')

        # create a test site
        site = Site.create_site('Test Site', 'foo', [british, french])
        self.assertTrue(site)

        # test languages were created properly
        lang = site.default_language
        self.assertEquals(lang, british)
        langs = site.get_languages()
        self.assertEquals(len(langs), 2)
        self.assertTrue(british in langs)
        self.assertTrue(french in langs)
        langs = site.get_languages('en')
        self.assertEquals(len(langs), 1)
        self.assertTrue(british in langs)

        # test adding and retrieving config
        site.add_config('foo', 'bar')
        values = site.get_config('foo')
        self.assertEquals(values[0], 'bar')
        self.assertEquals(len(values), 1)

        # add some child nodes
        child1 = site.doc_root.create_child('Child1', 'child1', {\
            french:('Enfant1', 'enfant1')})
        self.assertTrue(child1)
        child2 = site.doc_root.create_child('Child2', 'child2', {\
            french:('Enfant2', 'enfant2')})
        self.assertTrue(child2)
        grandchild1 = child1.create_child('Grandchild1', 'grandchild1', {\
            french:('Grandenfant1', 'grandenfant1')})
        self.assertTrue(grandchild1)
        grandchild2 = child1.create_child('Grandchild2', 'grandchild2', {\
            french:('Grandenfant2', 'grandenfant2')})
        self.assertTrue(grandchild2)

        # attempt to add with a bad slug
        self.assertRaises(BadSlug, site.doc_root.create_child, name='Child1', 
            slug='foo bar')

        # search for some paths, testing leading and trailing slashes ignored
        # properly and that right things are returned
        pp = site.parse_path('child1')
        self.assertEquals(pp.node, child1)
        self.assertEquals(pp.language, british)

        pp = site.parse_path('/child1')
        self.assertEquals(pp.node, child1)
        self.assertEquals(pp.language, british)

        pp = site.parse_path('/child1/')
        self.assertEquals(pp.node, child1)
        self.assertEquals(pp.language, british)

        pp = site.parse_path('/child1/grandchild2')
        self.assertEquals(pp.node, grandchild2)
        self.assertEquals(pp.language, british)

        # search for some paths using something besides default lang
        pp = site.parse_path('/enfant1/')
        self.assertEquals(pp.node, child1)
        self.assertEquals(pp.language, french)

        pp = site.parse_path('/enfant1/grandenfant2')
        self.assertEquals(pp.node, grandchild2)
        self.assertEquals(pp.language, french)

        # test path parser with a mismatched path
        pp = site.parse_path('/foo')
        self.assertEquals(pp.path, '/foo')
        self.assertEquals(pp.slugs_in_path, [])
        self.assertEquals(pp.slugs_after_item, ['foo'])
        self.assertEquals(pp.node, None)
        self.assertEquals(pp.page, None)
        self.assertEquals(pp.language, None)
        self.assertEquals(pp.item_type, ParsedPath.UNKNOWN)

        # test path parser with a good path, including bits past the node
        parsed = site.parse_path('/child1/grandchild2/foo/b')
        self.assertEquals(parsed.path, '/child1/grandchild2/foo/b')
        self.assertEquals(parsed.slugs_in_path, ['child1', 'grandchild2'])
        self.assertEquals(parsed.slugs_after_item, ['foo', 'b'])
        self.assertEquals(parsed.node, grandchild2)

        # test tree printing
        test_string = \
"""root (/)
   Child1 (child1)
      Grandchild1 (grandchild1)
      Grandchild2 (grandchild2)
   Child2 (child2)"""

        string = site.doc_root.tree_to_string()
        self.assertEquals(test_string, string)

        # test getting the path from a node
        test_string = "/child1/"
        string = child1.node_to_path()
        self.assertEquals(test_string, string)
        test_string = "/child1/grandchild2/"
        string = grandchild2.node_to_path()
        self.assertEquals(test_string, string)
