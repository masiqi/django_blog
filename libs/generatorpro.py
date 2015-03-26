"""Static file generator for Django."""

__version__ = '1.2Pro, 2008-02-12'

# The MIT License
# 
# Copyright (c) 2008 Jared Kuolt
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#
# 1.2Pro Version 2008-02-22
# Alrond (www.alrond.com)
#

import os
import shutil
from django.http import HttpRequest
from django.core.handlers.base import BaseHandler
from django.db.models.base import ModelBase
from django.db.models.manager import Manager
from django.db.models import Model
from django.db.models.query import QuerySet
from django.conf import settings
from django.utils.functional import Promise

class DummyHandler(BaseHandler):
    """Required to process request and response middleware"""
    
    def __call__(self, request):
        self.load_middleware()
        response = self.get_response(request)
        for middleware_method in self._response_middleware:
            response = middleware_method(request, response)
            
        return response    

class StaticGeneratorException(Exception):
    pass

class StaticGenerator(object):
    """
    The StaticGenerator class is created for Django applications, like a blog,
    that are not updated per request.
    
    Usage is simple::
    
        from generator import quick_publish
        quick_publish('/', Post.objects.live(), FlatPage)
        
    The class accepts a list of 'resources' which can be any of the 
    following: URL path (string), Model (class or instance), Manager, or 
    QuerySet.
    
    As of v1.1, StaticGenerator includes file and path deletion::
        
        from generator import quick_delete
        quick_delete('/page-to-delete/')
        
    The most effective usage is to associate a StaticGenerator with a model's
    post_save and post_delete signal.
    
    """
    
    def __init__(self, *resources):
        self.resources = self.extract_resources(resources)
        self.server_name = self.get_server_name()
        try:
            self.web_root = getattr(settings, 'WEB_ROOT')
        except AttributeError:
            raise StaticGeneratorException('You must specify WEB_ROOT in settings.py')
        
    def extract_resources(self, resources):
        """Takes a list of resources, and gets paths by type"""
        extracted = []
        for resource in resources:
            
            # A URL string
            if isinstance(resource, (str, unicode, Promise)):
                extracted.append(str(resource))
                continue
            
            # A model instance; requires get_absolute_url method
            if isinstance(resource, Model):
                extracted.append(resource.get_absolute_url())
                continue
            
            # If it's a Model, we get the base Manager
            if isinstance(resource, ModelBase):
                resource = resource._default_manager
            
            # If it's a Manager, we get the QuerySet
            if isinstance(resource, Manager):
                resource = resource.all()
            
            # Append all paths from obj.get_absolute_url() to list
            if isinstance(resource, QuerySet):
                extracted += [obj.get_absolute_url() for obj in resource]
        
        return extracted
        
    def get_server_name(self):
        try:
            return getattr(settings, 'SERVER_NAME')
        except:
            pass
            
        try:
            from django.contrib.sites.models import Site
            return Site.objects.get_current().domain
        except:
            print '*** Warning ***: Using "localhost" for domain name. Use django.contrib.sites or set settings.SERVER_NAME to disable this warning.'
            return 'localhost'
    
    def get_content_from_path(self, path):
        """
        Imitates a basic http request using DummyHandler to retrieve
        resulting output (HTML, XML, whatever)
        
        """
        request = HttpRequest()
        request.path = path
        request.META.setdefault('SERVER_PORT', 80)
        request.META.setdefault('SERVER_NAME', self.server_name)
        
        handler = DummyHandler()
        response = handler(request)
        
        return response.content
        
    def get_filename_from_path(self, path):
        """
        Returns (filename, directory)
        Creates index.html for path if necessary
        """
       # if path.endswith('/'):
       #     path = '%sindex.html' % path
	path = '%s/index.html' % path
            
        fn = os.path.join(self.web_root, path.lstrip('/'))
        return fn, os.path.dirname(fn)
        
    def publish_from_path(self, path):
        """
        Gets filename and content for a path, attempts to create directory if 
        necessary, writes to file.
        
        """
        fn, directory = self.get_filename_from_path(path)
        content = self.get_content_from_path(path)
        
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except:
                raise StaticGeneratorException('Could not create the directory: %s' % directory)
        
        try:
            f = open(fn, 'w')
            f.write(content)
            f.close()
        except:
            raise StaticGeneratorException('Could not create the file: %s' % fn)
            
    def delete_from_path(self, path):
        """Deletes file, attempts to delete directory"""
        fn, directory = self.get_filename_from_path(path)
        if not os.path.exists(directory):
            return True
        try:
            for file in os.listdir(directory):
                if file[:10] == "index.html":
                    os.remove(directory+"/"+file)
#           os.remove(fn)
        except:
            raise StaticGeneratorException('Could not delete file: %s' % fn)
            
        try:
            shutil.rmtree(directory)
        #except OSError:
        except :
            print 'Could not delete directory %s, likely because it is not empty.' % directory
            
            
    def do_all(self, func):
        return [func(path) for path in self.resources]
    
    def delete(self):
        return self.do_all(self.delete_from_path)
        
    def publish(self):
        return self.do_all(self.publish_from_path)

def quick_publish(*resources):
    return StaticGenerator(*resources).publish()
    
def quick_delete(*resources):
    return StaticGenerator(*resources).delete()

class ResponseStaticGenerator(object):
    def process_response(self, request, response):
        excluded = 0
        try:
            paths = getattr(settings, 'STATIC_GENERATOR_EXCLUDED')
            for p in paths:
                if request.path[:len(p)] == p:
                    excluded = 1
        except AttributeError:
            pass

        # in views.py to exlude: response['DisableStaticGenerator'] = 1
        try:
            disable = response['DisableStaticGenerator']
        except KeyError:
            disable = 0

	hostname = request.META.get('HTTP_HOST')
        if request.method == "GET" and response.status_code == 200 and not request.jrj.userid and not disable and not excluded:
            fn, directory =  StaticGenerator(request.path).get_filename_from_path(hostname + request.path)
            if request.GET:
                fn = fn + "?" + request.META['QUERY_STRING']
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                except:
                    raise StaticGeneratorException('Could not create the directory: %s' % directory)
            if not os.path.exists(fn):
                try:
                    f = open(fn, 'w')
                    f.write(response.content)
                    f.close()
                except:
                    raise StaticGeneratorException('Could not create the file: %s' % fn)
        return response
