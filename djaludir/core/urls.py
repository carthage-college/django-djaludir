from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    # alumni directory authentication
    url(r'^auth/', include("djaludir.auth.urls")),
    # alumni directory manager
    url(r'^manager/', include("djaludir.manager.urls")),
    # alumni registration
    url(r'^registration/', include("djaludir.registration.urls")),
    # home
    url(r'^$', "djaludir.core.views.home", name="alumni_directory_home"),
    # redirect
    #url(r'^$', RedirectView.as_view(url="/alumni/directory/home/")),
)
