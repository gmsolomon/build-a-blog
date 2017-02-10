#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                        autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogEntry(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class MainHandler(Handler):
    def render_front(self, title="", blog_post = "", error =""):
        blogs = db.GqlQuery("SELECT * FROM BlogEntry ORDER BY created DESC LIMIT 5;")
        self.render("front.html", title = title, blog_post = blog_post, error=error, blogs=blogs)
    def get(self):
    #    blogs = db.GqlQuery("SELECT * FROM BlogEntry ORDER BY created DESC LIMIT 5;")
        self.render_front()#("front.html", title = title, blog_post = blog_post, error=error, blogs=blogs)


#    def post(self):
#        title = self.request.get("title")
#        body = self.request.get("blog_post")

#        if title and body:
#            blog = BlogEntry (title = title, body = body)
#            blog.put()
#            self.redirect("/blog")
#        else:
#            error = "We need both a title and a blog post."
#            self.render_front(title, body, error)

class NewPost(Handler):
        def render_front(self, title="", blog_post = "", error =""):
            #blogs = db.GqlQuery("SELECT * FROM BlogEntry ORDER BY created DESC LIMIT 3;")
            self.render("blogentry.html", title = title, blog_post = blog_post, error=error)
        def get(self):
            self.render_front()

        def post(self):
            title = self.request.get("title")
            body = self.request.get("blog_post")

            if title and body:
                blog = BlogEntry (title = title, body = body)
                blog.put()
                blog_post_id = str(blog.key().id())
                #title = blog_post.title
                #body = blog_post.body
                self.redirect("/blog/" +blog_post_id)
            else:
                error = "We need both a title and a body."
                self.render_front(title, body, error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        #blog = db.GqlQuery("SELECT * FROM BlogEntry;")
        #self.response.write(id) #blog.get_by_id(id)) #replace this with some code to handle the request
        blog_post = BlogEntry.get_by_id(int(id))
        title = blog_post.title
        body = blog_post.body
        blog_id = blog_post.key().id()
        if blog_post:
            #self.render("blogentry.html", title = title, body = body, error="")
            #store template into a variable
            t = jinja_env.get_template("singleblog.html")
            content = t.render(blog_post = blog_post)
            #t = jinja
            #render our blog variables with template
            #response = t.render();
            #write out response
            self.response.out.write(content)
#<div class = "blog-title"><a href ="http://localhost:13080/blog/{{blog_post.key().id()}}">{{title}}</a></div>
            #self.response.write("<h1>"+ title+"</h1><br>" + body)
        else:
            self.response.write("There is no blog post with that id.")



app = webapp2.WSGIApplication([
    ('/blog', MainHandler),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
