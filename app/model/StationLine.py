from google.appengine.ext import db
from Prefecture import Prefecture
class StationLine(db.Model):
  prefecture          = db.ReferenceProperty(reference_class=Prefecture)
  station_line_number = db.IntegerProperty()
  station_line_name   = db.StringProperty()