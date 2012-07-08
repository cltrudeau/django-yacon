# yacon.curators.py

from django.conf import settings

if not hasattr(settings, 'YACON_USER_CURATOR'):
    # only define a UserCurator object if the user hasn't created their own
    from yacon.models.users import UserProfile
    from yacon.forms import UpdateUserForm, AddUserForm

    class UserCurator(object):
        profile_class = UserProfile
        update_form_class = UpdateUserForm
        add_form_class = AddUserForm
