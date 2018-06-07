from django.conf.urls import url

from djaludir.manager import views


urlpatterns = [
    url(
        r'^display/(?P<cid>\d+)/$', views.display,
        name="manager_alum_display"
    ),
    url(
        r'^search/$', views.search,
        kwargs={'messageSent':False},
        name='manager_search'
    ),
    url(
        r'^search/denied/$', views.search,
        kwargs={'permissionDenied':True},
        name='manager_search_denied'
    ),
    url(
        r'^search/sent/$', views.search,
        kwargs={'messageSent':True},
        name='manager_search_sent'
    ),
    url(
        r'^edit/(?P<cid>\d+)/$', views.edit,
        name='manager_user_edit'
    ),
    url(
        r'^edit/(?P<cid>\d+)/submit/$', views.edit,
        kwargs={'success':True},
        name='manager_user_edit_success'
    ),
    url(
        r'^update/', views.update,
        name='manager_user_update'
    ),
    url(
        r'^message/(?P<cid>\d+)/$', views.message,
        name='message_user'
    ),
    url(
        r'^send/$', views.send_message,
        name='send_message_user'
    ),
    url(
        r'^activity/$', views.search_activity,
        name='search_activity'
    ),
]
