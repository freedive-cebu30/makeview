import cgi
import os
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.ext import webapp
from User import User

class Album(db.Model):
  title           = db.StringProperty()
  post_code       = db.StringProperty()
  address         = db.StringProperty()
  station         = db.StringProperty()
  bus_stop        = db.StringProperty()
  start           = db.StringProperty()
  start_post_code = db.StringProperty()
  start_address   = db.StringProperty()
  pictureid       = db.IntegerProperty()
  time            = db.StringProperty()
  tag             = db.StringListProperty()
  tag_str         = db.StringProperty()
  search_index    = db.StringListProperty()
  timezone        = db.IntegerProperty()
  season          = db.IntegerProperty()
  recital         = db.TextProperty()
  point           = db.GeoPtProperty()
  point2          = db.GeoPtProperty()
  latitude        = db.StringProperty()
  longitude       = db.StringProperty()
  user            = db.ReferenceProperty(reference_class=User)
  openflg         = db.IntegerProperty()
  picture_max     = db.IntegerProperty()
  picture_counter = db.IntegerProperty()
  watch_counter   = db.IntegerProperty()
  registerDate    = db.DateTimeProperty(auto_now_add=True)
  updateDate      = db.DateTimeProperty(auto_now=True)


#  @property
#  def pictures(self):
#    return Picture.gql("WHERE album = :1", self.key())

#  @property
#  def SearchIndex(self):
#    return SearchIndex.gql("WHERE album = :1", self.key())


