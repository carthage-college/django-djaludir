from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    # my app
    url(r'^directory/', include(djaludir.directory.urls)),
    # redirect
    url(r'^$', RedirectView.as_view(url="/foobar/")),
)
