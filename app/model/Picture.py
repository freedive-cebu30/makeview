from google.appengine.ext import db
from User import User

class Picture(db.Model):
  name         = db.StringProperty()
  mime         = db.StringProperty()
  binary       = db.BlobProperty()
  user         = db.ReferenceProperty(reference_class=User)
  album        = db.ListProperty(db.Key)
  label        = db.StringProperty()
  registerDate = db.DateTimeProperty(auto_now_add=True)