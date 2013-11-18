from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.conf.urls import patterns, url

from djauth.views import loggedout

urlpatterns = patterns('',
    url(r'^login',auth_views.login,{'template_name': 'auth/login.html'}, name='auth_login'),
    url(r'^logout/$',auth_views.logout,{'next_page': reverse_lazy("auth_loggedout")}, name="auth_logout"),
    url(r'^loggedout',loggedout,{'template_name': 'auth/logged_out.html'}, name="auth_loggedout"),
    url(r'^$', RedirectView.as_view(url=reverse_lazy("auth_login"),), name="auth_home"),
)
