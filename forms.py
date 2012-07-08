# yacon.forms.py
#
import logging

from django import forms
from yacon.utils import get_user_attributes

logger = logging.getLogger(__name__)

# ============================================================================
# Forms
# ============================================================================

class UpdateUserForm(forms.Form):
    username = forms.CharField(max_length=30)
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
