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
#
import webapp2, os, jinja2, re
from google.appengine.ext import db

template_dir=os.path.join(os.path.dirname(__file__),'templates')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title=db.StringProperty(required=True)
    blog=db.TextProperty(required=True)
    created=db.DateTimeProperty(auto_now_add=True)

class MainPage(Handler):
    def render_front(self, title="", blog="", error=""):
        blogs=db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5;")
        self.render("main.html", title=title, blog=blog, error=error, blogs=blogs)

    def get(self):
        self.render_front()

class NewPostPage(MainPage):
    def render_front(self, title="", blog="", error=""):
        self.render("new-post.html", title=title, blog=blog, error=error)

    def get(self):
        self.render_front()

    def post(self):
        title=self.request.get("title")
        blog=self.request.get("blog")

        if title and blog:
            b=Blog(title=title, blog=blog)
            b.put()
            self.redirect('/')
        else:
            error = "We need both a Title and Blog."
            self.render_front(title, blog, error)

class BlogPage(MainPage):
    def render_front(self, title="", blog="", error=""):
        blogs=db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC ;")
        self.render("blog.html", title=title, blog=blog, error=error, blogs=blogs)

    def get(self):
        self.render_front()

class IndBlogPage(Handler):
    def get(self, id):
        """ Render a page with post determined by the id (via the URL/permalink) """

        blog = Blog.get_by_id(int(id))
        if blog:
            t = jinja_env.get_template("permalink.html")
            response = t.render(blog=blog)
        else:
            error = "there is no post with id %s" % id
            t = jinja_env.get_template("404.html")
            response = t.render(error=error)

        self.response.out.write(response)
    #def get(self, id):
    #    pass
    #    self.response.write(id)
        #key=db.Key.from_path('Post', int(id))
        #post=db.get(key)

        #if not post:
        #    self.error('404')
        #    return
        #self.render('permalink.html', blog=post)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', BlogPage),
    webapp2.Route('/blog/<id:\d+>', IndBlogPage),
    ('/new', NewPostPage)
    ], debug=True)
