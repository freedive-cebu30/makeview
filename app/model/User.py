from google.appengine.ext import db
class User(db.Model):
  name                = db.StringProperty()
  nickname            = db.StringProperty()
  email               = db.StringProperty()
  age                 = db.IntegerProperty()
  sex                 = db.IntegerProperty()#1 man 2 weman 3 other
  post_code           = db.StringProperty()
  address             = db.StringProperty()
  telFirst            = db.StringProperty()
  telSecond           = db.StringProperty()
  telThird            = db.StringProperty()
  googleAccount       = db.UserProperty()
  twitterAccount      = db.StringProperty()
  delegate            = db.StringProperty()
  chargePerson        = db.StringProperty()
  capital             = db.IntegerProperty()
  corporateFlg        = db.IntegerProperty()# 2 company
  corporate           = db.StringProperty()
  recital             = db.TextProperty()
  mapflg              = db.IntegerProperty()#1 close or 2 open
  albumList           = db.StringListProperty()
  accessFlg           = db.IntegerProperty()
  loginCounter        = db.IntegerProperty()
  contentPicture      = db.IntegerProperty()#byte
  contentPictureLimit = db.IntegerProperty()#sum_byte_limit
  registerDate        = db.DateTimeProperty(auto_now=True)
  updateDate          = db.DateTimeProperty(auto_now_add=True)
