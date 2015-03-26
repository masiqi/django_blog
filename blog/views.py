from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from blog.models import Category, Blog, UserSettings
from tagging.models import Tag, TaggedItem
from blog.forms import WriteBlogForm, ProfileForm, WriteCommentForm
from blog.utils import username2id, relationship, _get_perm
import pyjrj as jrj

def index(request, template_name="blog/index.html"):
    print request.jrj.userid
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
    
def channel_index(request, template_name="blog/index.html"):
    print request.jrj.userid
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

def user_index(request, category_id=None, tag_id=None):
    userid, username, perm, buid, ut = _get_perm(request)
    template_name = settings.USER_TEMPLATE_PATH % ut.template_id
    
    category = None
    tag = None
    blogs = Blog.objects.select_related().filter(user__userid=buid, status=1).order_by("-id")
    if category_id is not None:
        category = Category.objects.get(pk=category_id)
        blogs = blogs.filter(category__id=category_id)
    if tag_id is not None:
        tag = Tag.objects.get(pk=tag_id)
        blogs = TaggedItem.objects.get_by_model(Blog, tag).filter(user__userid=buid, status=1).order_by("-id")

    return render_to_response(template_name, {
        'category': category,
        'tag': tag,
        'usersettings': ut,
        'username': username,
        'perm': perm,
        'blogs': blogs,
    }, context_instance=RequestContext(request))
    
def read_blog(request, blog_id, form_class=WriteCommentForm):
    userid, username, perm, buid, ut = _get_perm(request)
    template_name = settings.BLOG_TEMPLATE_PATH % ut.template_id   
    
    try:
        blog = Blog.objects.select_related().get(pk=blog_id)
    except Blog.DoesNotExist :
        raise Http404
    #print blog.comments
    form = form_class(initial={'blog':blog.id})
    return render_to_response(template_name, {
        'usersettings': ut,
        'username': username,
        'perm': perm,
        'blog': blog,
        'form': form,
    }, context_instance=RequestContext(request))
    
def edit_blog(request, blog_id, template_name="blog/edit_blog.html", form_class=WriteBlogForm):
    userid, username, perm, buid, ut = _get_perm(request)
    if userid != buid:
        raise Http404
    blog = Blog.objects.get(pk=blog_id)    
    if request.method == "POST":
        form = form_class(ut.user, request.POST, instance=blog)
        if form.is_valid():
            print form.cleaned_data
            blog = form.save(commit=False)
            blog.user = ut.user
            blog.save()
            return HttpResponseRedirect(reverse("blog_user_index"))      
    else:
        form = form_class(user=ut.user, instance=blog)
    return render_to_response(template_name, {
        'blog': blog,
        'form': form,
        'usersettings': ut,
        'username': username,
        'perm': perm,        
    }, context_instance=RequestContext(request))
    
@jrj.require_login()
def write_blog(request, template_name="blog/write_blog.html", form_class=WriteBlogForm):
    userid, username, perm, buid, ut = _get_perm(request)
    if userid != buid:
        raise Http404
    if request.method == "POST":
        form = form_class(ut.user, request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.user = ut.user
            blog.save()
            return HttpResponseRedirect(reverse("blog_user_index"))      
    else:
        form = form_class(user=ut.user)
    return render_to_response(template_name, {
        'form': form,
        'usersettings': ut,
        'username': username,
        'perm': perm,        
    }, context_instance=RequestContext(request)) 
    
def write_comment(request, template_name="blog/write_comment.html", form_class=WriteCommentForm):
    #userid, username, perm, buid, ut = _get_perm(request)
    #if userid != buid:
    #    raise Http404
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            comment = form.save()
            return HttpResponseRedirect(reverse("blog_read", args=[comment.blog_id]))
        else:
            print "xxxxxxxxxxxxxx"
            return render_to_response(template_name, {
                'form': form,
            }, context_instance=RequestContext(request)) 
    print "fuck"
    return render_to_response(template_name, {

    }, context_instance=RequestContext(request)) 

@jrj.require_login()
def profile(request, template_name="blog/profile.html", form_class=ProfileForm):
    userid, username, perm, buid, ut = _get_perm(request)
    if userid != buid:
        raise Http404
    if request.method == "POST":
        form = form_class(ut.user, request.POST, instance=ut)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.user = ut.user
            blog.save()
            return HttpResponseRedirect(reverse("blog_user_index"))      
    else:
        form = form_class(user=ut.user, instance=ut)
    return render_to_response(template_name, {
        'form': form,
        'usersettings': ut,
        'username': username,
        'perm': perm,        
    }, context_instance=RequestContext(request))     
    
    
@jrj.require_login()
def delete_blog(request, template_name="blog/delete_blog.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

@jrj.require_login()
def delete_comment(request, template_name="blog/delete_comment.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
    
@jrj.require_login()
def create_category(request, template_name="blog/delete_comment.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

