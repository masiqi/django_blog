from django.contrib.syndication.feeds import Feed
from blog.models import Category, Blog
from django.core.urlresolvers import reverse
from blog.utils import _get_perm

class LatestEntries(Feed):
    title = ""
    link = "/"
    description = ""
    #title_template = "feeds/latest_entries_title.html"

    def __init__(self, slug, request):
        userid, username, perm, buid, ut = _get_perm(request)
        super(LatestEntries, self).__init__(slug, request)
        self.title = ut.name
        self.description = ut.depict
        self.buid = buid
    
    def items(self):
        return Blog.objects.filter(user__userid=self.buid, status=1).order_by('-id')[:5]
    
    def description(self, obj):
        return obj.content
    
    def item_link(self, item):
        return "http://%s%s" % (self.request.META.get('HTTP_HOST'), reverse("blog_read", args=[item.id]))
    
    
