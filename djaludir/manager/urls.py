from django.conf.urls import patterns, url

urlpatterns = patterns('djaludir.manager.views',
    url(r'^display/(?P<student_id>\d+)/$','display', name="manager_alum_display"),
    url(r'^search/$','search', kwargs={'messageSent':False}, name="manager_search"),
    url(r'^search/denied/$', 'search', kwargs={'permissionDenied':True}, name="manager_search_denied"),
    url(r'^search/sent/$','search', kwargs={'messageSent':True}, name="manager_search_sent"),
    url(r'^edit/(?P<student_id>\d+)/$','edit', name="manager_user_edit"),
    url(r'^edit/(?P<student_id>\d+)/submit/$','edit', kwargs={'success':True}, name="manager_user_edit_success"),
    url(r'^update', 'update', name='manager_user_update'),
    url(r'^message/(?P<student_id>\d+)/$', 'message', name="message_user"),
    url(r'^send/$', 'send_message', name="send_message_user"),
    url(r'^activity/$','search_activity', name="search_activity"),
)