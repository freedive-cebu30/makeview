import cgi
import os
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.ext import webapp

class Inquiry(db.Model):
  name    = db.StringProperty()
  email   = db.StringProperty()
  title   = db.StringProperty()
  content = db.StringProperty()