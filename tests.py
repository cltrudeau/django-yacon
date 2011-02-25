# yacon.tests.py
# blame ctrudeau chr(64) arsensa.com

import unittest
from yacon.models.hierarchy import ContentHierarchy, BadSlug, PathNotFound

# ============================================================================
# ContentHierachy Test Cases
# ============================================================================

class ContentHierarchyTestCase(unittest.TestCase):
    def test_tree(self):
        # create and return the root
        root = ContentHierarchy.get_root()
        self.assertTrue(root)

        # first call in test will have run the create code, second call should
        # run the retrieve code
        root = ContentHierarchy.get_root()
        self.assertTrue(root)

        # add some children to root
        child1 = root.add_child(name='Child1', slug='child1')
        self.assertTrue(child1)
        child2 = root.add_child(name='Child2', slug='child2')
        self.assertTrue(child2)
        grandchild1 = child1.add_child(name='Grandchild1', slug='grandchild1')
        self.assertTrue(grandchild1)
        grandchild2 = child1.add_child(name='Grandchild2', slug='grandchild2')
        self.assertTrue(grandchild2)

        ContentHierarchy.output_tree()

        # attempt to add with a bad slug
        self.assertRaises(BadSlug, root.add_child, name='Child1', 
            slug='foo bar')

        # search for a path
        find = ContentHierarchy.node_from_path('child1')
        self.assertEquals(find, child1)
        find = ContentHierarchy.node_from_path('/child1')
        self.assertEquals(find, child1)
        find = ContentHierarchy.node_from_path('/child1/')
        self.assertEquals(find, child1)
        find = ContentHierarchy.node_from_path('/child1/grandchild2')
        self.assertEquals(find, grandchild2)

        # make sure a bad path causes an exception
        self.assertRaises(PathNotFound, ContentHierarchy.node_from_path, '/foo')
        self.assertRaises(PathNotFound, ContentHierarchy.node_from_path, 
            '/child1/foo')

        # test that path parser with a mismatched path
        parsed = ContentHierarchy.parse_path('/foo')
        self.assertEquals(parsed.path, '/foo')
        self.assertEquals(parsed.slugs_in_path, [])
        self.assertEquals(parsed.slugs_after_node, ['foo'])
        self.assertEquals(parsed.node, None)

        # test that path parser with a good path
        parsed = ContentHierarchy.parse_path('/child1/grandchild2/foo/b')
        self.assertEquals(parsed.path, '/child1/grandchild2/foo/b')
        self.assertEquals(parsed.slugs_in_path, ['child1', 'grandchild2'])
        self.assertEquals(parsed.slugs_after_node, ['foo', 'b'])
        self.assertEquals(parsed.node, grandchild2)

        # test tree printing
        test_string = \
"""root (/)
   Child1 (child1)
      Grandchild1 (grandchild1)
      Grandchild2 (grandchild2)
   Child2 (child2)"""

        string = root.tree_to_string()
        self.assertEquals(test_string, string)

        # test getting the path from a node
        test_string = "/child1/"
        string = child1.node_to_path()
        self.assertEquals(test_string, string)
        test_string = "/child1/grandchild2/"
        string = grandchild2.node_to_path()
        self.assertEquals(test_string, string)

# ============================================================================
# Page Test Cases
# ============================================================================

from django.core import management
from yacon.models.pages import Page, page_list

class PageTestCase(unittest.TestCase):
    def setUp(self):
        # load test data
        management.call_command('create_test_data')

        # fetch pages explicitly for test comparisons
        self.health = ContentHierarchy.node_from_path('/articles/health/')
        self.steak = Page.objects.get(node=self.health, slug='steak')
        self.smoking = Page.objects.get(node=self.health, slug='smoking')

    def test_tree(self):
        # test invalid URI
        pages = page_list('/foo/bar')
        self.assertEquals(pages, [])

        # test URI with a slug in it
        pages = page_list('/articles/health/steak')
        self.assertEquals(pages, [self.steak])

        # test URI without a slug
        pages = page_list('/articles/health/')
        self.assertEquals(len(pages), 2)
        self.assertTrue(self.steak in pages)
        self.assertTrue(self.smoking in pages)
