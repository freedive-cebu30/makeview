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

PICTUREPAGE = 15
ALBUMPICTURE = 4

class AdminUserInsertHandler(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/user','insert.html')
    html = template.render(fpath,'')
    self.response.out.write(html)
  def get(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/user','insert.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

    return

class AdminUserInsertEndHandler(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    formList = ['name',
                'nickname',
                'email',
                'age',
                'sex',
                'postCode',
                'address',
                'telFirst',
                'telSecond',
                'telThird',
                'corporateFlg',
                'corporate',
                'delegate',
                'chargePerson',
                'capital',
                'mapflg',
                'recital'
                ]
    formData={}
    for list in formList:
      formData[list] = self.request.get(list)

    data = User()
    try:
      if len(formData['name'])==0:
        raise NameError
      data.name         = formData['name']
      if len(formData['nickname'])==0:
        raise NicknameNameError
      data.nickname     = formData['nickname']
      data.email        = formData['email']
      data.age          = int(formData['age'])
      data.sex          = int(formData['sex'])
      data.post_code    = formData['postCode']
      data.address      = formData['address']
      data.telFirst     = formData['telFirst']
      data.telSecond    = formData['telSecond']
      data.telThird     = formData['telThird']
      data.corporateFlg = int(formData['corporateFlg'])
      data.delegate     = formData['delegate']
      data.chargePerson = formData['chargePerson']
      data.capital      = int(formData['capital'])
      data.corporate    = formData['corporate']
      data.mapflg       = int(formData['mapflg'])
      data.recital      = formData['recital']

      data.put()

      fpath = os.path.join(os.path.dirname(__file__),'template/admin/user','insertend.html')
      html = template.render(fpath,'')
      self.response.out.write(html)
    except:
      self.errorFunc()
  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/admin','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

class AdminUserGetAddress(webapp.RequestHandler):
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


class AdminUserUpdateHandler(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    id = self.request.get('id')
    datas = User.get_by_id(long(id))
    params = {'datas':datas}
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/user','update.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

class AdminUserUpdateEndHandler(webapp.RequestHandler):

    def post(self):
      user = users.get_current_user()
      if not user:
          return self.redirect('/admin/index')
      formList = ['name',
                  'nickname',
                  'email',
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

      id = self.request.get('id')
      data = User.get_by_id(long(id))

      try:
        if len(formData['name'])==0:
          raise NameError
        data.name         = formData['name']
        if len(formData['nickname'])==0:
          raise NicknameNameError
        data.nickname     = formData['nickname']
        data.email        = formData['email']
        data.address      = formData['address']
        data.telFirst     = formData['telFirst']
        data.telSecond    = formData['telSecond']
        data.telThird     = formData['telThird']
        data.age          = int(formData['age'])
        data.sex          = int(formData['sex'])
        data.delegate     = formData['delegate']
        data.chargePerson = formData['chargePerson']
        data.capital      = int(formData['capital'])
        data.corporateFlg = int(formData['corporateFlg'])
        data.corporate    = formData['corporate']
        data.recital      = formData['recital']

        data.put()

        fpath = os.path.join(os.path.dirname(__file__),'template/admin/user','updateend.html')
        html = template.render(fpath,'')
        self.response.out.write(html)
      except:
        self.errorFunc()

    def errorFunc(self):
      fpath = os.path.join(os.path.dirname(__file__),'template/admin','error.html')
      html = template.render(fpath,'')
      self.response.out.write(html)

      return

class AdminUserListHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    company = self.request.get('company')
    if company == "2":
      datas = db.GqlQuery("SELECT * FROM User WHERE corporateFlg=2")
    else:
      datas = db.GqlQuery("SELECT * FROM User WHERE corporateFlg=1")

    params = {'datas':datas}
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/user','list.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminUserDetailHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    id = self.request.get('userid')
    datas = User.get_by_id(long(id))
    params = {'datas':datas}
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/user','detail.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminUserShowPictureHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    page = self.request.get('page')
    try:
        page = int(page) - 1
    except:
        page = 0
    userid = self.request.get('userid')
    datas = User.get_by_id(long(userid))

    paginator = ObjectPaginator(datas.picture_set,PICTUREPAGE)
    if page>=paginator.pages:
            page = paginator.pages - 1
    params = {
        "datas"  : paginator.get_page(page),
        "pages"  : range(1,paginator.pages+1),
        "page"   : page+1,
        "userid" : datas
    }
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/user','showpicture.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminUserShowAlbumHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
    #############PICTURE#######################
    picturepage = self.request.get('picturepage')
    if picturepage =='':
      if cookie.has_key('picturepage'):
        picturepage = cookie['picturepage'].value.decode('utf-8')
    else:
      cookie['picturepage'] = picturepage.encode('utf-8')
      cookie['picturepage']['expires'] = 3600

    try:
        picturepage = int(picturepage) - 1
    except:
        picturepage = 0
    userid = self.request.get('userid')
    datas = User.get_by_id(long(userid))
    params = {'datas':datas}

    paginator = ObjectPaginator(datas.picture_set,PICTUREPAGE)
    if picturepage>=paginator.pages:
            picturepage = paginator.pages - 1
    ##############PICTURE_END#####################
    ##############ALBUM#########################

    albumpage = self.request.get('albumpage')
    if albumpage =='':
      if cookie.has_key('albumpage'):
        albumpage = cookie['albumpage'].value.decode('utf-8')
    else:
      cookie['albumpage'] = albumpage.encode('utf-8')
      cookie['albumpage']['expires'] = 3600

    print cookie.output()
    try:
        albumpage = int(albumpage) - 1
    except:
        albumpage = 0

    albumpaginator = ObjectPaginator(datas.album_set,ALBUMPICTURE)
    if albumpage>=albumpaginator.pages:
        albumpage = albumpaginator.pages - 1

    params = {
        "datas"        : paginator.get_page(picturepage),
        "picturepages" : range(1,paginator.pages+1),
        "picturepage"  : picturepage+1,
        "userid"       : datas,
        "albumdatas"   : albumpaginator.get_page(albumpage),
        "albumpages"   : range(1,albumpaginator.pages+1),
        "albumpage"    : albumpage+1
    }

    fpath = os.path.join(os.path.dirname(__file__),'template/admin/user','showalbum.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminUserDeleteConfirmHandler(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    id = self.request.get('id')
    datas = User.get_by_id(long(id))
    params = {'datas':datas}
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/user','deleteconfirm.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return


class AdminUserDeleteEndHandler(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    id = self.request.get('id')
    data = User.get_by_id(long(id))
    data.delete()
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/user','deleteend.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

    return


