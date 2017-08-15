from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.conf.urls import url

from djaludir.registration import views


urlpatterns = [
    url(
        r'^create/ldap/$',
        views.create_ldap, name='registration_create_ldap'
    ),
    url(
        r'^modify/ldap/password/$',
        views.modify_ldap_password, name='registration_modify_ldap_password'
    ),
    url(
        r'^search/informix/$',
        views.search_informix, name='registration_search_informix'
    ),
    url(
        r'^search/ldap/$',
        views.search_ldap, name='registration_search_ldap'
    ),
    url(
        r'^search/$',
        views.search_home, name='registration_search'
    ),
    # redirect
    url(
        r'^$',
        RedirectView.as_view(url=reverse_lazy('registration_search'),),
        name='registration_home'
    )
]
