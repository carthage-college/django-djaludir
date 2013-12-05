from django.conf.urls import patterns, url

urlpatterns = patterns('djaludir.manager.views',
    url(r'^display/(?P<student_id>\d+)/$','display', name="manager_alum_display"),
    url(r'^search/$','search', name="manager_search"),
    url(r'^edit/(?P<student_id>\d+)/$','edit', name="manager_user_edit"),
    url(r'^edit/(?P<student_id>\d+)/submit/$','edit', kwargs={'success':True}, name="manager_user_edit_success"),
    url(r'^update', 'update', name='manager_user_update'),
    url(r'^activity/$','search_activity', name="search_activity"),
)
