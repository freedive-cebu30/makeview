from google.appengine.ext import db
class Prefecture(db.Model):
  prefecture_number = db.IntegerProperty()
  prefecture_name   = db.StringProperty()