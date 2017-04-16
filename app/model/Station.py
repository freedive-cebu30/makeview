from google.appengine.ext import db
from StationLine import StationLine
class Station(db.Model):
  station_line   = db.ReferenceProperty(reference_class=StationLine)
  station_number = db.IntegerProperty()
  station_name   = db.StringProperty()
