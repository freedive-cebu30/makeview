from google.appengine.ext import db
class Sum(db.Model):
  album_counter       = db.IntegerProperty()
  registerDate        = db.DateTimeProperty(auto_now=True)
  updateDate          = db.DateTimeProperty(auto_now_add=True)
