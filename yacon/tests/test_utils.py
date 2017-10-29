from django.contrib.auth.models import User
from django.test import TestCase

from yacon.utils import (get_user_attributes, SummarizedPage, get_profile,
    get_system_text)

from yacon.models.pages import Page
from yacon.models.users import UserProfile
from yacon.tests.utils import create_test_site

# ============================================================================

class Bourbons(object):
    # object for testing utils.get_user_attributes()
    QUIET_MAN = True
    BULLEIT = True

    def is_yummy(self):
        return True


class ProblemAttr(object):
    # to test fail cases of utils.get_user_attributes() we need a property
    # that raises an AttributeError when called with getattr()

    @property
    def cause_problem(self):
        raise AttributeError

# ----------------------------------------------------------------------------

class UtilTests(TestCase):
    def setUp(self):
        pass

    def test_summarizedpage(self):
        create_test_site()

        page = Page.objects.first()

        # test basic functionality
        s = SummarizedPage(page, 'blurb', 10)
        self.assertEqual('This is a', s.summary)

        # test bad block key handling
        s = SummarizedPage(page, 'foo', 10)
        self.assertEqual('', s.summary)

        # ---- test the utility method that does the cutting

        #       ---12345678901234567---8901----234567890----
        text = '<p>This is a string <b>with</b> bolding.</p>'

        # test html cutting and space handling, cut mid-way through # "bolding"
        result = SummarizedPage.summarize(text, 24)
        self.assertEqual('This is a string with', result)

        # test text smaller than summary
        result = SummarizedPage.summarize(text, 40)
        self.assertEqual('This is a string with bolding.', result)

        # test text without a space
        result = SummarizedPage.summarize('<p>no_spaces_here</p>', 3)
        self.assertEqual('no_', result)

    def test_get_user_attributes(self):
        b = Bourbons()
        result = get_user_attributes(b)

        # order not guarnateed, check length and convert to sets for comparison
        self.assertEqual(2, len(result))
        self.assertEqual(set(['QUIET_MAN', 'BULLEIT']), set(result))

        result = get_user_attributes(b, False)
        self.assertEqual(3, len(result))
        self.assertEqual(set(['QUIET_MAN', 'BULLEIT', 'is_yummy']), set(result))

        # check error handling
        p = ProblemAttr()
        result = get_user_attributes(p)
        self.assertEqual([], result)

    def test_get_profile(self):
        create_test_site()

        # base case
        user = User.objects.get(username='fflintstone')
        expected = UserProfile.objects.get(user=user)

        profile = get_profile(user)
        self.assertEqual(expected, profile)

        # error case
        profile = get_profile(None)
        self.assertEqual(None, profile)

    def test_get_system_text(self):
        from yacon.conf import SITE, TEXT

        # base case
        SITE['text']= {
            'en':{
                'foo':'bar'
            }   
        }

        result = get_system_text('en', 'foo')
        self.assertEqual('bar', result)

        # site lang error
        result = get_system_text('fr', 'show_page')
        self.assertEqual(TEXT['show_page'], result)

        # text key error
        result = get_system_text('fr', 'foo')
        self.assertTrue(result.startswith('Text Error for'))
