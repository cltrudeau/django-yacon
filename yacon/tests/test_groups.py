from django.test import TestCase
from django.contrib.auth.models import User, Group

from yacon.models.groupsq import GroupOfGroups, OwnedGroupOfGroups

# ============================================================================
# GroupOfGroups Test Cases
# ============================================================================

class GroupOfGroupsTestCase(TestCase):
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
