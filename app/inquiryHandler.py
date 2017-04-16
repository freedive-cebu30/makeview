import cgi
import os
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from model.Inquiry import Inquiry

class InquiryInsertHandler(webapp.RequestHandler):
  def post(self):

    user = users.get_current_user()
    if user is not None:
      title   = self.request.get('title')
      content = self.request.get('content')
      data = Inquiry()

      data.name     = user.nickname()
      data.email    = user.email()
      data.title    = title
      data.content  = content
      key = data.put()
      params = {}
      fpath = os.path.join(os.path.dirname(__file__),'template/user','inquiryinsertend.html')
      html = template.render(fpath,params)
      self.response.out.write(html)


class InquiryFormHandler(webapp.RequestHandler):

  def get(self):
    params = {}

    fpath = os.path.join(os.path.dirname(__file__),'template/user','inquiry.html')
    html = template.render(fpath,params)
    self.response.out.write(html)
