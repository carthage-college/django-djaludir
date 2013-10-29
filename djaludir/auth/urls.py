from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.conf.urls import patterns, url

urlpatterns = patterns('djaludir.auth.views',
    url(r'^login/$','login', name="login"),
    url(r'^logout/$','logout', name="logout"),
    # redirect
    url(r'^$', RedirectView.as_view(url=reverse_lazy("login"),), name="auth_home"),
)
