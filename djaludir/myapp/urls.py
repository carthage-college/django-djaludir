from django.conf.urls.defaults import *
from django.contrib import admin

#django discovery
admin.autodiscover()

urlpatterns = patterns('',
    (r'^alumni/directory/display/(?P<student_id>\d+)/$','djaludir.alumni.views.display'),
    (r'^alumni/directory/search/$','djaludir.alumni.views.search'),
    (r'^alumni/admin/(.*)', admin.site.root),
)