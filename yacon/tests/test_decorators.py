from django.test import TestCase, Client
from django.contrib.auth.models import User
from unittest.mock import Mock

from yacon import decorators
from yacon.tests.utils import create_test_site

# ============================================================================

@decorators.superuser_required
def superuser_view(request):
    return 'Got Here'

# ----------------------------------------------------------------------------

class DecoratorTests(TestCase):
    def setUp(self):
        create_test_site()
        self.client = Client()

    def test_superuser_required(self):
        request = Mock()

        # admin should be allowed
        request.user = User.objects.get(username='admin')
        self.client.force_login(request.user)
        result = superuser_view(request)
        self.assertEqual(result, 'Got Here')

        # Fred should not be allowed, URI for login redirect should get called
        request.user = User.objects.get(username='fflintstone')
        superuser_view(request)
        request.build_absolute_uri.assert_called()
