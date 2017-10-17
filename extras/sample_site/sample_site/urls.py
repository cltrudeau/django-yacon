from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout

from django.views import static
from yacon.views import content

urlpatterns = [
    # Examples:
    # url(r'^$', 'sample_site.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^accounts/login/$', login, {'template_name':'admin/login.html'}),
    url(r'^accounts/logout/$', logout, {'next_page':'/'}),
    url(r'admin/logout/$', logout, {'next_page':'/'}),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^media/(?P<path>.*)$', static.serve, {
        'document_root': settings.MEDIA_ROOT, }),

    url(r'^pmedia/(.*)$', content.django_private_serve),

    url(r'^yacon/', include('yacon.urls')),
    url(r'^$', content.display_page),

    # URL Eater, should always be last
    url(r'^(.*)/$', content.display_page),
]
