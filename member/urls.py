from django.conf.urls.defaults import *

urlpatterns = patterns('member.views',
    url(r'^$', 'index', name='member_index'),
    url(r'^(?P<userid>\d+)$', 'show', name='member_show'),    
)
