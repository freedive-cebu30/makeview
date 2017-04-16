import cgi
import os
import wsgiref.handlers
import sys
import string
import xmlrpclib

from django.core.paginator import ObjectPaginator, InvalidPage
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from Cookie import SimpleCookie
from model.User import User
from model.Album import Album
from django.utils import simplejson
from model.PictureConnectAlbum import PictureConnectAlbum

class userGetAddress(webapp.RequestHandler):
  def get(self):
    server = xmlrpclib.ServerProxy("http://yubin.senmon.net/service/xmlrpc/")
    postcode = self.request.get('postCode')
    try:
        data = server.yubin.fetchAddressByPostcode(postcode)
        for da in data:
          datas = "{"+da["pref"]+da["city"]+da["town"]+"}"
        json = simplejson.dumps(datas, ensure_ascii=False)
        self.response.content_type = 'application/json'
        self.response.out.write(json)


    except xmlrpclib.Fault, fault:
          print "[%s] #%s %s" % (postcode, fault.faultCode, fault.faultString)


class UserUpdateHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user is None:
      return self.redirect('/index')

    email = user.email()
    gqlUserData = db.GqlQuery("SELECT * FROM User WHERE email='"+email+"'")
    for user in gqlUserData:
      userid = user.key().id()
    userData = User.get_by_id(long(userid))
    params = {'datas':userData}

    fpath = os.path.join(os.path.dirname(__file__),'template/user/user','update.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

class UserUpdateEndHandler(webapp.RequestHandler):
    def post(self):
      try:
        user = users.get_current_user()
        if user is None:
            return self.redirect('/index')
        formList = ['name',
                    'address',
                    'telFirst',
                    'telSecond',
                    'telThird',
                    'age',
                    'sex',
                    'delegate',
                    'chargePerson',
                    'capital',
                    'corporateFlg',
                    'corporate',
                    'recital'
                  ]
        formData={}
        for list in formList:
          formData[list] = self.request.get(list)

        email = user.email()
        gqlUserData = db.GqlQuery("SELECT * FROM User WHERE email='"+email+"'")
        for user in gqlUserData:
          userid = user.key().id()
        userData = User.get_by_id(long(userid))

        userData.name         = formData['name']
        userData.address      = formData['address']
        userData.telFirst     = formData['telFirst']
        userData.telSecond    = formData['telSecond']
        userData.telThird     = formData['telThird']
        if formData['age'] !="":
          userData.age          = int(formData['age'])
        if formData['sex'] !="":
          userData.sex          = int(formData['sex'])
        userData.delegate     = formData['delegate']
        userData.chargePerson = formData['chargePerson']
        if formData['capital'] !="":
          userData.capital      = int(formData['capital'])
        if formData['corporateFlg'] !="":
          userData.corporateFlg = int(formData['corporateFlg'])
        userData.corporate    = formData['corporate']
        userData.recital      = formData['recital']

        userData.put()

        fpath = os.path.join(os.path.dirname(__file__),'template/user/user','updateend.html')
        html = template.render(fpath,'')
        self.response.out.write(html)
      except:
        self.errorFunc()

    def errorFunc(self):
      fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
      html = template.render(fpath,'')
      self.response.out.write(html)

      return
