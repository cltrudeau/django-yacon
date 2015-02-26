# yacon.curators.py

from yacon.models.users import UserProfile
from yacon.forms import UpdateUserForm, AddUserForm

class UserCurator(object):
    profile_class = UserProfile
    update_form_class = UpdateUserForm
    add_form_class = AddUserForm
