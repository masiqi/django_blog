from django.conf.urls.defaults import *

from django.contrib import admin
from blog.feeds import LatestEntries
admin.autodiscover()

feeds = {
    'latest': LatestEntries,
    #'categories': LatestEntriesByCategory,
}

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
    #(r'^(.*)', include('blog.urls')),
    #(r'^api/', include('blog.api')),
)

urlpatterns += patterns('blog.views',
    url(r'^channel/$', 'channel_index', name='blog_index'),
    url(r'^$', 'user_index', name='blog_user_index'),
    url(r'^(?P<blog_id>\d+)_a.html$', 'read_blog', name='blog_read'),
    url(r'^(?P<blog_id>\d+)_e.html$', 'edit_blog', name='blog_edit'),
    url(r'^(?P<category_id>\d+)_c.html$', 'user_index', name='blog_user_category'),
    url(r'^(?P<tag_id>\d+)_t.html$', 'user_index', name='blog_user_tag'),
    url(r'^write$', 'write_blog', name='blog_write'),
    url(r'^write_comment$', 'write_comment', name='blog_writecomment'),
    url(r'^profile$', 'profile', name='blog_profile'),
)

urlpatterns += patterns('',
    (r'^feeds/(?P<url>.*)$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
)

urlpatterns += patterns('',
    (r'^api/', include('blog.api')),
)

handler404 = 'blog.views.channel_index'

