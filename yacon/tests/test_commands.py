from django.test import TestCase

from yacon.models.site import Site
from yacon.tests.utils import create_test_site

# ============================================================================
# Yacon Management Commands Test Cases
# ============================================================================

class ManagementCommands(TestCase):
    def setUp(self):
        create_test_site()

    def test_check_commands(self):
        # check that the 'blah' site was created
        site = Site.objects.get(name='my_name')
        self.assertTrue(site)

        # check that the default site was created
        site = Site.objects.get(name='Localhost Site')
        self.assertTrue(site)

        # check that test data was created
        pp = site.parse_path('/articles/health/')
        self.assertTrue(pp.node)
