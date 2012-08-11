# yacon.views.users_panel.py
#
# Methods for the Users Panel
#

import logging

from django.contrib.auth.forms import AdminPasswordChangeForm
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from yacon import conf
from yacon.decorators import superuser_required
from yacon.models.common import Language
from yacon.models.users import UsernameError

logger = logging.getLogger(__name__)

# ============================================================================

@superuser_required
def list_users(request):
    sort_by = request.GET.get('sort', 'user__username')
    direction = request.GET.get('direction')

    sort_args = filter(None, sort_by.split(','))
    if direction == 'rev':
        sort_args = ['-%s' % arg for arg in sort_args]

    curator = conf.custom.user_curator
    profiles = curator.profile_class.objects.all().order_by(*sort_args)
    data = {
        'title':'User Listing',
        'profiles':profiles,
        'default_sort':'user__username',
    }

    return render_to_response('nexus/list_users.html', data, 
        context_instance=RequestContext(request))


@superuser_required
def edit_user(request, profile_id):
    profile = get_object_or_404(USER_CURATOR.profile_class, id=profile_id)

    if request.method == 'POST':
        form = USER_CURATOR.update_form_class(request.POST)
        if form.is_valid():
            try:
                profile.update_profile(form.cleaned_data)
                return HttpResponseRedirect('/yacon/nexus/users/list_users/')
            except UsernameError:
                errors = form._errors.setdefault('username', ErrorList())
                errors.append('Username already exists')
    else: # GET
        form = USER_CURATOR.update_form_class(user=profile.user, 
            profile=profile)

    data = {
        'title':'Edit User',
        'profile':profile,
        'form':form,
    }

    return render_to_response('nexus/edit_user.html', data, 
        context_instance=RequestContext(request))


@superuser_required
def add_user(request):
    if request.method == 'POST':
        form = USER_CURATOR.add_form_class(request.POST)
        if form.is_valid():
            try:
                USER_CURATOR.profile_class.create_from_data(form.cleaned_data)
                return HttpResponseRedirect('/yacon/nexus/users/list_users/')
            except UsernameError:
                errors = form._errors.setdefault('username', ErrorList())
                errors.append('Username already exists')
    else: # GET
        form = USER_CURATOR.add_form_class()

    data = {
        'title':'Add User',
        'form':form,
        'clear_autocomplete':True,
    }

    return render_to_response('nexus/edit_user.html', data, 
        context_instance=RequestContext(request))


@superuser_required
def user_password(request, profile_id):
    profile = get_object_or_404(USER_CURATOR.profile_class, id=profile_id)

    if request.method == 'POST':
        form = AdminPasswordChangeForm(profile.user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/yacon/nexus/users/list_users/')
    else: # GET
        form = AdminPasswordChangeForm(profile.user)

    data = {
        'title':'Change User Password',
        'profile':profile,
        'form':form,
        'clear_autocomplete':True,
    }

    return render_to_response('nexus/edit_user.html', data, 
        context_instance=RequestContext(request))
