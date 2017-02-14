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
    # creats a database for the blog entries
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

def get_posts(num_limit, num_offset):
    # retrieves the number of posts (num_limit) that the MainHandler has requested

    blog_list = db.GqlQuery("SELECT * FROM BlogEntry ORDER BY created DESC LIMIT %s OFFSET %s;" % (num_limit, num_offset))
    return blog_list

class MainHandler(Handler):
 # displays the blogs main page with the five most recent blog posts
 # currents set to display only the first page of the blog_post
 # plan to add pagination at a later date

    def get(self, title="", blog_post = "", error =""):
        blog_query = db.GqlQuery("SELECT * FROM BlogEntry ORDER BY created DESC")
        page_number = 1
        num_offset = page_number * 5 - 5
        blogs = get_posts(5, num_offset)
        self.render("front.html", title = title, blog_post = blog_post, error=error, blogs=blogs)



class NewPost(Handler):
    # handler for /newpost to enter a new blog post
        def render_front(self, title="", blog_post = "", error =""):
            self.render("blogentry.html", title = title, blog_post = blog_post, error=error)

        def get(self):
            self.render_front()

        def post(self):
            title = self.request.get("title")
            body = self.request.get("blog_post")
            #make sure user enters blog title and blog entry otherwise will generate an error
            if title and body:
                blog = BlogEntry (title = title, body = body)
                blog.put()
                blog_post_id = str(blog.key().id())
                self.redirect("/blog/" +blog_post_id)
            else:
                error = "We need both a title and a body."
                self.render_front(title, body, error)

class Redirect(webapp2.RequestHandler):
    #redirects / to /blog
    def get(self):
        self.redirect("blog")

class ViewPostHandler(Handler):
    # views individual post on its own page user the post entry's id
    def get(self, id):
        blog_post = BlogEntry.get_by_id(int(id))
        if blog_post:
            self.render("singleblog.html", blog_post= blog_post)
        else:
#            self.response.write("There is no blog post with that id.")
            error = "There is no blog post with that id."
            self.render("singleblog.html", blog_post = "" , error = error )


app = webapp2.WSGIApplication([
    ('/', Redirect),
    ('/blog', MainHandler),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
