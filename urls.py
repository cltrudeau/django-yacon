from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^SeniorityLiving/', include('SeniorityLiving.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)

if settings.YACON_STATIC_SERVE and (settings.YACON_ADMIN_ENABLED or 
    settings.YACON_EXAMPLES_ENABLED):
    # enable static serving of pages for admin and examples
    import os
    cur_dir = os.path.dirname(__file__)
    static_root = os.path.join(cur_dir, 'static_media')

    urlpatterns += patterns('',
        (r'^static_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root':static_root}),
    )

if settings.YACON_ADMIN_ENABLED:
    urlpatterns += patterns('',
        (r'^admin/content_listing/$', 'yacon.views.admin.content_listing'),
        (r'^admin/page_info/(\d+)/$', 'yacon.views.admin.page_info'),
        (r'^$', direct_to_template, {'template':'admin/index.html'}),
    )

if settings.YACON_EXAMPLES_ENABLED:
#    urlpatterns += patterns('',
#        (r'^content_listing/$', 'yacon.views.user.content_listing'),
#    )
    pass
