from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sample_site.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^accounts/login/$', login, {'template_name':'admin/login.html'}),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^yacon/', include('yacon.urls')),
    url(r'^$', 'yacon.views.content.display_page'),
    url(r'^(.*)/$', 'yacon.views.content.display_page'),
)
