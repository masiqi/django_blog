from django.http import HttpResponse

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

def require_login(next=None, internal=None):
    def decorator(view):
        def newview(request, *args, **kwargs):
            next = newview.next
            internal = newview.internal

            try:
                jrj = request.jrj
            except:
                raise ImproperlyConfigured('Make sure you have the Jrj middleware installed.')
            if not jrj.check_session(request):
                return jrj.redirect("www.jrj.com.cn")
            return view(request, *args, **kwargs)
        newview.next = next
        newview.internal = internal
        return newview
    return decorator

class Jrj(object):
    def __init__(self, jrj_userid):
        self.userid = jrj_userid
        
    def hello(self):
        print "hello %s !" % self.jrj_userid
        
    def check_session(self, request):
        if self.userid:
            return True
        else:
            return False
        
    def redirect(self, url):
        return HttpResponse('<jrj:redirect url="%s" />' % (url, ))

class JrjMiddleware(object):
    def process_request(self, request): 
        _thread_locals.jrj = request.jrj = Jrj(request.REQUEST.get('jrj_user_id'))
        if 'jrj_userid' in request.session:
            request.jrj.userid = request.session['jrj_userid']
    
    def process_response(self, request, response):
        if request.jrj.userid:
            request.session['jrj_userid'] = request.jrj.userid
        return response
        
