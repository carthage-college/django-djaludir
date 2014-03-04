from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.conf.urls import patterns, url

urlpatterns = patterns('djaludir.registration.views',
    url(
        r'^create/ldap/$',
        'create_ldap', name="registration_create_ldap"
    ),
    url(
        r'^update/ldap/password/$',
        'update_ldap_password', name="registration_update_ldap_password"
    ),
    url(
        r'^search/informix/$',
        'search_informix', name="registration_search_informix"
    ),
    url(
        r'^search/ldap/$',
        'search_ldap', name="registration_search_ldap"
    ),
    url(
        r'^search/$',
        'search_home', name="registration_search"
    ),
    # redirect
    url(
        r'^$',
        RedirectView.as_view(url=reverse_lazy("registration_search"),),
        name="registration_home"
    ),
)
