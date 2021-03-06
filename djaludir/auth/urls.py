from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.conf.urls import url

from djauth.views import loggedout
from djaludir.auth import views


urlpatterns = [
    url(
        r'^login/$', views.login_user, name='auth_login'
    ),
    url(
        r'^logout/$', auth_views.logout,
        {'next_page': reverse_lazy('auth_loggedout')},
        name='auth_logout'
    ),
    url(
        r'^loggedout/$', loggedout,
        name='auth_loggedout'
    ),
    url(
        r'^$',
        RedirectView.as_view(url=reverse_lazy('auth_login')),
        name='auth_home'
    )
]
