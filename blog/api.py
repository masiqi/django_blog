from django.conf.urls.defaults import *
from django_restapi.model_resource import Collection
from django_restapi.responder import XMLResponder
from django_restapi.receiver import FormReceiver
from django_restapi.authentication import HttpBasicAuthentication
from blog.models import Blog
from blog.utils import username2id
from blog.forms import WriteBlogForm



class myCollection(Collection):
    
    def __call__(self, request, *args, **kwargs):
        userid = username2id(request.META.get('BLOG_USER'))
        self.queryset = Blog.objects.filter(user__userid=userid)
        return super(myCollection, self).__call__(request, *args, **kwargs)

mymodel_resource = myCollection(
    queryset = Blog.objects.all(),
    permitted_methods = ('GET', 'POST', 'DELETE'),
    #authentication = HttpBasicAuthentication(),
    receiver = FormReceiver(),
    responder = XMLResponder(paginate_by = 10), 
    form_class = WriteBlogForm
)

urlpatterns = patterns('',
    url(r'^(.*?)/?$', mymodel_resource)    
)
