# yacon.forms.py
#
import logging

from django import forms

from yacon.definitions import TITLE_LENGTH, SLUG_LENGTH
from yacon.utils import get_user_attributes

logger = logging.getLogger(__name__)

# ============================================================================
# Forms
# ============================================================================

class UpdateUserForm(forms.Form):
    username = forms.RegexField(max_length=30, regex=r'^[\w.@+-]+$',
        error_messages = {'invalid':('Only letters, numbers and the characters '
            '@ . + - _ are allowed.')})
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=75)
    is_active = forms.BooleanField(required=False, initial=True)
    is_staff = forms.BooleanField(required=False)
    is_superuser = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        if 'initial' not in kwargs:
            initial =  {}

        if 'user' in kwargs:
            user = kwargs.pop('user')
            initial.update({
                'username':user.username,
                'first_name':user.first_name,
                'last_name':user.last_name,
                'email':user.email,
                'is_active':user.is_active,
                'is_staff':user.is_staff,
                'is_superuser':user.is_superuser,
            })

        if 'profile' in kwargs:
            profile = kwargs.pop('profile')

            for attr in get_user_attributes(profile):
                if attr == 'user':
                    continue

                initial[attr] = getattr(profile, attr)

        kwargs['initial'] = initial
        super(UpdateUserForm, self).__init__(*args, **kwargs)


class AddUserForm(UpdateUserForm):
    password1 = forms.CharField(max_length=30, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=30, widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(AddUserForm, self).clean()
        if 'password1' not in cleaned_data or 'password2' not in cleaned_data:
            raise forms.ValidationError('Password cannot be empty')

        if cleaned_data['password1'] != cleaned_data['password2']:
            raise forms.ValidationError('Password mismatch')

        return cleaned_data


class CreatePageForm(forms.Form):
    title = forms.CharField(max_length=TITLE_LENGTH)
    slug = forms.CharField(max_length=SLUG_LENGTH, required=False)
    auto_slug = forms.BooleanField(required=False)
    hidden = forms.BooleanField(required=False)

    EXPECTED_FIELDS = ('title', 'slug', 'auto_slug', 'csrfmiddlewaretoken')

    def __init__(self, *args, **kwargs):
        super(CreatePageForm, self).__init__(*args, **kwargs)

        self.fields['auto_slug'].widget = forms.widgets.HiddenInput()
        auto_slug = self.initial.get('auto_slug', False)
        if auto_slug:
            self.fields['slug'].widget = forms.widgets.HiddenInput()

        # populate the extra fields passed in, args0=POST
        if args and args[0]:
            for key, value in args[0].items():
                if key in self.EXPECTED_FIELDS:
                    continue

                self.fields[key] = forms.CharField(required=False)


    def clean(self):
        data = super(CreatePageForm, self).clean()
        if not data['auto_slug'] and not data['slug']:
            # auto slug not specified but slug not given
            raise forms.ValidationError('slug field cannot be empty')

        return data
