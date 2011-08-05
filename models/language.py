# yacon.models.language.py
# blame ctrudeau chr(64) arsensa.com

import logging
from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)

# ============================================================================
# Language Class
# ============================================================================

class Language(models.Model):
    """This model defines languages that are acceptable in the Yacon CMS.  A
    language is made up of a language identifier which itself can be a
    language code with an optional addition of a country code for variations.

    For more on language identifiers and codes, see:

    http://www.i18nguy.com/unicode/language-identifiers.html
    """

    name = models.CharField(max_length=25)
    identifier = models.CharField(max_length=25)

    class Meta:
        app_label = 'yacon'

    # --------------------------------------------
    # Getters
    @classmethod
    def default_language(cls):
        """Retrieves the default language for the installation (note this is
        different from the default language for an individual Site.  This is
        retrieved from the django settings file, if not found then 'en' is
        returned

        @returns: string with default language identifier
        """
        default = settings.LANGUAGE_CODE

        lang = None
        if default:
            try:
                lang = cls.objects.get(identifier=default)
                return lang
            except cls.DoesNotExist:
                # the default language doesn't exist as a class, create it
                try:
                    lang_dict = dict(settings.LANGUAGES)
                    lang = cls(name=lang_dict[default], identifier=default)
                    lang.save()
                    return lang
                except KeyError:
                    # setting wasn't in language dictionary, do nothing and
                    # we'll build the default one
                    pass

        # else: no language in settings file, create english
        lang = cls(name='English', identifier='en')
        lang.save()

        return lang
