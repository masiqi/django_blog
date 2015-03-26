from django.conf import settings
from blog.models import UserSettings

def _get_perm(request):
    userid = request.jrj.userid
    username = request.META.get('BLOG_USER')
    perm = 0
        
    try:
        buid = username2id(username)
    except:
        raise Http404
    if userid is not None:
        perm = relationship(buid, userid)
            
    ut, created = UserSettings.objects.get_or_create(user__userid=buid, defaults={'user_id': buid, 'name': username, 'depict': username, 'template_id':settings.DEFAULT_TEMPLATE_ID})
    return userid, username, perm, buid, ut

def username2id(username):
    return username

def relationship(u1, u2):
    if u1 == u2:
        return 3
    elif is_friend(u1, u2):
        return 2
    elif is_follower(u1, u2):
        return 1
    else:
        return 0
    
def is_follower(u1, u2):
    return True

def is_friend(u1, u2):
    return True
