from django.db import models
from django.contrib import admin

class User(models.Model):
    userid = models.IntegerField('userid', primary_key=True)
    
    def __unicode__(self):
        return str(self.userid)
    
admin.site.register(User)  
