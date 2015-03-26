from django.db import models
from django.contrib import admin
from django.db.models import signals
from generatorpro import quick_delete

from member.models import User
from tagging.fields import TagField
from tagging.models import Tag

BLOG_STATUS = (
    ("0", "sketch"),
    ("1", "published"),
    ("2", "blocked"),
)

BLOG_DISPLAY_TYPE = (
    ("0", "content"),
    ("1", "summary"),
    ("2", "title"),
)

BLOG_INDEX_PERM = (
    ("0", "all"),
    ("1", "follower"),
    ("2", "friends"),
    ("3", "myself"),
)

BLOG_READ_PERM = (
    ("0", "all"),
    ("1", "follower"),
    ("2", "friends"),
    ("3", "myself"),
)

BLOG_COMMENT_PERM = (
    ("0", "all"),
    ("1", "follower"),
    ("2", "friends"),
    ("3", "myself"),
)

class Category(models.Model):
    user = models.ForeignKey(User, db_index=True)
    name = models.CharField('name', max_length=32)

    def __unicode__(self):
        return unicode(str(self.user) + '.' + self.name)

    class Meta:
        unique_together = (("user", "name"),)
        verbose_name_plural = 'categories'

class Blog(models.Model):
    user = models.ForeignKey(User, db_index=True)
    category = models.ForeignKey(Category, db_index=True)
    title = models.CharField('title', max_length=128)
    summary = models.TextField('summary', null=True)
    content = models.TextField('content', null=True)
    created_at = models.DateTimeField('create date', db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField('update date', db_index=True, auto_now=True)    
    status = models.SmallIntegerField(choices=BLOG_STATUS, default=0, db_index=True) 
    read_perm = models.SmallIntegerField(choices=BLOG_READ_PERM, default=0)
    comment_perm = models.SmallIntegerField(choices=BLOG_COMMENT_PERM, default=0)
    tags = TagField(null=True, blank=True)
    
    def __unicode__(self):
        return unicode(str(self.user) + '.' + self.title)
    
    def getLeft(self):
        blogs = Blog.objects.filter(user=self.user, id__lt=self.id).order_by("-id")[0:1]
        for blog in blogs:
            return blog
        return None
    
    def getRight(self):
        blogs = Blog.objects.filter(user=self.user, id__gt=self.id)[0:1]
        for blog in blogs:
            return blog
        return None
    
    def getDomain(self):
        return "%s.nb.jrj.com.cn" % str(self.user_id)
    
    
class Template(models.Model):
    name = models.CharField('name', max_length=32)
    path = models.CharField('path', max_length=64)
    
    def __unicode__(self):
        return unicode(self.name)
    
class UserSettings(models.Model):
    user = models.OneToOneField(User, db_index=True)
    name = models.CharField('blog name', max_length=16)
    depict = models.CharField('blog depict', max_length=64)
    display = models.SmallIntegerField(choices=BLOG_DISPLAY_TYPE, default=0)
    entries = models.SmallIntegerField(default=10)
    template = models.ForeignKey(Template) 
    perm = models.SmallIntegerField(choices=BLOG_INDEX_PERM, default=0)   

class Comment(models.Model):
    user = models.ForeignKey(User, db_index=True, null=True)
    blog = models.ForeignKey(Blog, db_index=True, related_name='comments')
    content = models.TextField('content', null=True)
    created_at = models.DateTimeField('create date', db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField('update date', db_index=True, auto_now=True)
    
    def __unicode__(self):
        return unicode(self.blog)
    
    def getDomain(self):
        return "%s.nb.jrj.com.cn" % str(self.blog.user_id)            

class Keyword(models.Model):
    name = models.CharField('name', max_length=32)

    def __unicode__(self):
        return unicode(self.name)
    
class Counter(models.Model):
    pass

def delete_blog(sender, instance, **kwargs):
    print instance
    quick_delete(instance.getDomain())
    
def delete_comment(sender, instance, **kwargs):
    print instance
    quick_delete(instance.getDomain())
    
signals.post_save.connect(delete_blog, sender=Blog)
signals.post_save.connect(delete_comment, sender=Comment)

admin.site.register(Category)
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(Template)
admin.site.register(UserSettings)