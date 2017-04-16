import cgi
import os
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.ext import webapp
from Picture import Picture
from Album import Album

class PictureConnectAlbum(db.Model):
  picture         = db.ReferenceProperty(Picture, required=True)
  album           = db.ReferenceProperty(Album, required=True)
  username        = db.StringProperty()
  picture_comment = db.StringProperty()
  order_picture   = db.IntegerProperty()
  #order_picture   = db.IntegerProperty(required=True)
  #picture_max     = db.IntegerProperty(required=True)
 # picture_number  = db.IntegerProperty()
  #watch_number    = db.IntegerProperty()