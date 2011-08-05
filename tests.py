# yacon.tests.py
# blame ctrudeau chr(64) arsensa.com

from django.utils import unittest
from yacon.models.language import Language
from yacon.models.site import Site, PathNotFound
from yacon.models.hierarchy import Node, BadSlug

# ============================================================================
# Yacon Management Commands Test Cases
# ============================================================================

class ManagementCommands(unittest.TestCase):
    def setUp(self):
        management.call_command('yacon_add_site', 'blah', 'blah')
        management.call_command('yacon_create_defaults')
        management.call_command('yacon_create_test_data')

    def test_check_commands(self):
        # check that the 'foo' site was created
        site = Site.objects.get(name='blah')
        self.assertTrue(site)

        # check that the default site was created
        site = Site.objects.get(name='Localhost Site')
        self.assertTrue(site)

        # check that test data was created
        node = site.node_from_path('/articles/health/')
        self.assertTrue(node)

# ============================================================================
# Site and Hierachy Test Cases
# ============================================================================

class SiteTestCase(unittest.TestCase):
    def test_hierarchy(self):
        english = Language(name='GB English', identifier='en-gb')
        english.save()
        french = Language(name='French', identifier='fr')
        french.save()

        # create a test site
        site = Site.create_site('Test Site', 'foo', [english, french])
        self.assertTrue(site)

        # test languages were created properly
        lang = site.default_language
        self.assertEquals(lang, english)
        langs = site.get_languages()
        self.assertEquals(len(langs), 2)
        self.assertTrue(english in langs)
        self.assertTrue(french in langs)
        langs = site.get_languages('en')
        self.assertEquals(len(langs), 1)
        self.assertTrue(english in langs)

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
        (find, lang) = site.node_lang_from_path('child1')
        self.assertEquals(find, child1)
        self.assertEquals(lang, english)
        (find, lang) = site.node_lang_from_path('/child1')
        self.assertEquals(find, child1)
        self.assertEquals(lang, english)
        (find, lang) = site.node_lang_from_path('/child1/')
        self.assertEquals(find, child1)
        self.assertEquals(lang, english)
        (find, lang) = site.node_lang_from_path('/child1/grandchild2')
        self.assertEquals(find, grandchild2)
        self.assertEquals(lang, english)

        # search for some paths using something besides default lang
        (find, lang) = site.node_lang_from_path('/enfant1/')
        self.assertEquals(find, child1)
        self.assertEquals(lang, french)
        (find, lang) = site.node_lang_from_path('/enfant1/grandenfant2')
        self.assertEquals(find, grandchild2)
        self.assertEquals(lang, french)

        # make sure a bad path causes an exception
        self.assertRaises(PathNotFound, site.node_from_path, '/foo')
        self.assertRaises(PathNotFound, site.node_from_path, '/child1/foo')

        # test path parser with a mismatched path
        parsed = site.parse_path('/foo')
        self.assertEquals(parsed.path, '/foo')
        self.assertEquals(parsed.slugs_in_path, [])
        self.assertEquals(parsed.slugs_after_node, ['foo'])
        self.assertEquals(parsed.node, None)

        # test path parser with a good path, including bits past the node
        parsed = site.parse_path('/child1/grandchild2/foo/b')
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

        string = site.doc_root.tree_to_string()
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
        # test data was loaded during the ManagementCommands test, use that
        # data to test page interactions, start by getting some of the nodes
        # and pages themselves
        self.site = Site.objects.get(name='Localhost Site')
        self.health = self.site.node_from_path('/articles/health/')
        self.steak = Page.objects.get(node=self.health, slug='steak')
        self.smoking = Page.objects.get(node=self.health, slug='smoking')

    def test_tree(self):
        # test invalid URI
        pages = page_list(self.site, '/foo/bar')
        self.assertEquals(pages, [])

        # test URI with a slug in it
        pages = page_list(self.site, '/articles/health/steak')
        self.assertEquals(pages, [self.steak])

        # test URI without a slug
        pages = page_list(self.site, '/articles/health/')
        self.assertEquals(len(pages), 2)
        self.assertTrue(self.steak in pages)
        self.assertTrue(self.smoking in pages)


# ============================================================================
# GroupOfGroups Test Cases
# ============================================================================

from django.contrib.auth.models import User, Group
from yacon.models.groupsq import GroupOfGroups, OwnedGroupOfGroups

class GroupOfGroupsTestCase(unittest.TestCase):
    def _user(self, username, email, password):
        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            u = User.objects.create_user(username, email, password)

        return u

    def _group(self, name, users):
        try:
            g = Group.objects.get(name=name)
        except Group.DoesNotExist:
            g = Group(name=name)
            g.save()

            for user in users:
                user.groups.add(g)
                user.save()

        return g

    def setUp(self):
        # create some users and groups for testing
        self.homer = self._user('homer', 'homer@powerplant.com', 'password')
        self.lenny = self._user('lenny', 'lenny@powerplant.com', 'password')
        self.carl = self._user('carl', 'carl@powerplant.com', 'password')
        self.waylon = self._user('waylon', 'waylon@powerplant.com', 'password')
        self.montgomery = self._user('montgomery', 'montgomery@powerplant.com', 
            'password')
        self.hans = self._user('hans', 'hans@powerplant.com', 'password')
        self.fritz = self._user('fritz', 'fritz@powerplant.com', 'password')

        users = [self.homer, self.lenny, self.carl]
        self.powerplant_peons = self._group('powerplant_peons', users)

    def test_gog(self):
        # create a new gog and put a user in it
        powerplant_owners = GroupOfGroups(name='powerplant_owners')
        powerplant_owners.save()
        powerplant_owners.add(self.montgomery)

        # test the has_user functionality
        result = powerplant_owners.has_user(self.montgomery)
        self.assertTrue(result)

        # test the list user functionality
        users = powerplant_owners.list_users()
        self.assertEquals(len(users), 1)
        self.assertTrue(self.montgomery in users)

        # create a new gog and add it as a subrelation
        germans = GroupOfGroups(name='germans')
        germans.save()
        germans.add(self.hans)
        germans.add(self.fritz)

        powerplant_owners.add(germans)

        # test the has_user functionality for the nested group
        result = powerplant_owners.has_user(self.hans)
        self.assertTrue(result)

        # test the list user functionality
        users = powerplant_owners.list_users()
        self.assertEquals(len(users), 3)
        self.assertTrue(self.montgomery in users)
        self.assertTrue(self.hans in users)
        self.assertTrue(self.fritz in users)

        # create a new gog that has a user, a group and a nested gog
        powerplant_employees = GroupOfGroups(name='powerplant_employees')
        powerplant_employees.save()
        powerplant_employees.add(self.waylon)
        powerplant_employees.add(powerplant_owners)
        powerplant_employees.add(self.powerplant_peons)

        # test the has_user functionality for each type of item
        result = powerplant_employees.has_user(self.waylon)
        self.assertTrue(result)
        result = powerplant_employees.has_user(self.hans)
        self.assertTrue(result)
        result = powerplant_employees.has_user(self.homer)
        self.assertTrue(result)

        # test the list user functionality
        users = powerplant_employees.list_users()
        self.assertEquals(len(users), 7)
        self.assertTrue(self.montgomery in users)
        self.assertTrue(self.hans in users)
        self.assertTrue(self.fritz in users)
        self.assertTrue(self.waylon in users)
        self.assertTrue(self.homer in users)
        self.assertTrue(self.lenny in users)
        self.assertTrue(self.carl in users)

    def test_owned_group(self):
        homer_friends = OwnedGroupOfGroups(owner=self.homer, name='friends')
        homer_friends.save()
        homer_friends.add(self.lenny)
        homer_friends.add(self.carl)

        hans_friends = OwnedGroupOfGroups(owner=self.hans, name='friends')
        hans_friends.save()
        hans_friends.add(self.fritz)

        tests = OwnedGroupOfGroups.objects.filter(owner=self.homer, 
            name='friends')
        friends = tests[0].list_users()
        self.assertEquals(len(friends), 2)
        self.assertTrue(self.lenny in friends)
        self.assertTrue(self.carl in friends)
