from django.conf.urls import patterns, url

urlpatterns = patterns('djaludir.manager.views',
    url(r'^display/(?P<student_id>\d+)/$','display', name="alumna_display"),
    url(r'^search/$','search', name="manager_search"),
    url(r'^edit/(?P<student_id>\d+)/$','edit', name="user_edit"),
    url(r'^activity/$','search_activity', name="search_activity"),
)
