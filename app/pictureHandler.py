import cgi
import os
import operator
import wsgiref.handlers
import math
import hashlib
import random
from django.core.paginator import ObjectPaginator, InvalidPage
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from model.Picture import Picture
from model.User import User
from model.PictureConnectAlbum import PictureConnectAlbum
from model.Album import Album
from Cookie import SimpleCookie
FILE_MAX = 100
PAGE     = 16
#DOMAIN = "localhost:8084"
PROTOCOLHTTP = "http://"
PROTOCOLHTTPS = "https://"
DOMAIN = "make-view.appspot.com"

class PictureInsertHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user is None:
      return self.redirect('/index')
    else:
      logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")

    if user:
      loginFlg = 1

    num = random.randint(1, 1000000)
    tooken = num

    cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
    cookie['picturetooken'] = tooken
    cookie['picturetooken']['expires'] = 3600
    print cookie.output()

    params = {'logout_link' : logout_link,
              'loginFlg'    : loginFlg,
              'tooken'      : tooken
              }
    fpath = os.path.join(os.path.dirname(__file__),'template/user/picture','insert.html')
    html = template.render(fpath, params)
    self.response.out.write(html)

    return

class PictureInsertEndHandler(webapp.RequestHandler):
  def post(self):
    try:
      user = users.get_current_user()
      if user is None:
        return self.redirect('/index')
      else:
        logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")

      cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
      if cookie.has_key('picturetooken'):
        tooken = cookie['picturetooken'].value

      cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
      cookie['picturetooken'] = ""
      cookie['picturetooken']['expires'] = 3600
      print cookie.output()
      hiddenToken = self.request.get('tooken')
      if tooken != hiddenToken:
        #return self.redirect('/user/picture/insert')
        raise

      i=0
      while(i < 9):
        binary = self.request.get('binary_'+str(i))
        #print len(binary)
        if not binary:
          break
        name = self.request.body_file.vars['binary_'+str(i)].filename
        mime = self.request.body_file.vars['binary_'+str(i)].headers['content-type']
        self.registerPicture(binary,name,mime,user)
        i += 1

      if user:
        loginFlg = 1
      params = {'logout_link' : logout_link,
                'loginFlg'    : loginFlg
              }
      fpath = os.path.join(os.path.dirname(__file__),'template/user/picture','insertend.html')
      html = template.render(fpath,params)
      self.response.out.write(html)
    except:self.errorFunc()

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

    return

  def registerPicture(self,binary,name,mime,user):
    email = user.email()
    userData = db.GqlQuery("SELECT * FROM User WHERE email='"+email+"'")
    data = Picture()
    data.name    = name
    data.mime    = mime
    for user in userData:
      id = user.key().id()
    user = User.get_by_id(long(id))
    data.user = user
    data.binary  = db.Blob(binary)
    contentPicture = user.contentPicture;
    if contentPicture is None:
      contentPicture = 0
    user.contentPicture = contentPicture+len(binary)/1000
    data.put()
    user.put()

class PictureUpdateEndHandler(webapp.RequestHandler):
    def post(self):
      try:
        user = users.get_current_user()
        if user is None:
          return self.redirect('/index')
        else:
          logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
        cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
        picturHandlerePage = self.request.get('picturHandlerePage')

        cookie['picturHandlerePage'] = picturHandlerePage.encode('utf-8')
        cookie['picturHandlerePage']['expires'] = 3600
        print cookie.output()

        pictureIdList =  self.request.POST.getall("pictureid")

        for pil in pictureIdList:
          label      = self.request.get("label"+pil)
          if len(label) > 10:
            raise RuntimeError("labelMax error")
          data       = Picture.get_by_id(long(pil))
          data.label = label
          data.put()

        return self.redirect('/user/picture/list')
      except:
        self.errorFunc()

    def errorFunc(self):
      fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
      html = template.render(fpath,'')
      self.response.out.write(html)

class PictureListHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user is None:
      return self.redirect('/index')
    else:
      logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
    page               = self.request.get('page')
    zoomFlg            = self.request.get('zoomFlg')
    searchLabel        = self.request.get('searchLabel')
    picturHandlerePage = self.request.get('picturHandlerePage')
    delFlg             = self.request.get('delFlg')

    cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
    if delFlg != "1":
      if searchLabel != "":
        cookie['picturHandlerePage'] = ""
        cookie['searchLabel'] = searchLabel.encode('utf-8')
        cookie['searchLabel']['expires'] = 3600
        print cookie.output()
      else:
        if cookie.has_key('searchLabel'):
          searchLabel = cookie['searchLabel'].value.decode('utf-8')
    else:
      searchLabel = ""
      picturHandlerePage = ""
      cookie['searchLabel'] =""
      cookie['picturHandlerePage'] =""
      print cookie.output()

    #############PICTURE#######################

    if picturHandlerePage =='':
      if cookie.has_key('picturHandlerePage'):
        picturHandlerePage = cookie['picturHandlerePage'].value.decode('utf-8')
    else:
      cookie['picturHandlerePage'] = picturHandlerePage.encode('utf-8')
      cookie['picturHandlerePage']['expires'] = 3600
      print cookie.output()
    try:
      picturHandlerePage = int(picturHandlerePage) - 1
    except:
      picturHandlerePage = 0

    email = user.email()
    userData = db.GqlQuery("SELECT * FROM User WHERE email='"+email+"'")
    for user in userData:
      userid = user.key().id()
    userDatas = User.get_by_id(long(userid))
    userPictureDatas = userDatas.picture_set

    datas = list()
    keyList = list()
    for PictureData in userPictureDatas:
      keyList.append(PictureData.key().id())
    if searchLabel !="":
      PictureDatas = Picture.gql("WHERE label =:1", searchLabel)
      for PictureData in PictureDatas:
        if PictureData.key().id() in keyList:
          datas.append(PictureData)
    else:
      for upd in userPictureDatas:
        datas.append(upd)
    datas.sort(key=operator.attrgetter('registerDate'))
    datas.reverse()

    pictureCount = len(datas)
    pagerFlg = 0
    if pictureCount > PAGE:
      pagerFlg = 1;

    lastPage = int(math.ceil(float(pictureCount)/PAGE))
    if picturHandlerePage > lastPage:
      picturHandlerePage = lastPage
    #pager
    #now page picturepage+1
    #last page paginator.pages+1
    page1 = 1
    if picturHandlerePage+1 > 2:
      page1 = picturHandlerePage+1-1
    elif picturHandlerePage+1 > 3:
      page1 = picturHandlerePage+1-2
    if picturHandlerePage+1 == lastPage+1:
      page1 = page1-3
    elif picturHandlerePage == lastPage+1:
      page1 = page1-2

    if page1 < 2:
      page1 = 2

    pages = range(page1-1,lastPage+1)

    paginator = ObjectPaginator(datas,PAGE)
    if picturHandlerePage>=paginator.pages:
      picturHandlerePage = paginator.pages - 1
    if user:
      loginFlg = 1

    params = {
        "datas"       : paginator.get_page(picturHandlerePage),
        "pages"       : pages,
        "page"        : picturHandlerePage+1,
        "prev"        : picturHandlerePage,
        "next"        : picturHandlerePage+2,
        "pagerFlg"    : pagerFlg,
        "lastpage"    : lastPage,
        'zoomFlg'     : zoomFlg,
        'searchLabel' : searchLabel,
        'loginFlg'    : loginFlg,
        'logout_link' : logout_link
    }

    fpath = os.path.join(os.path.dirname(__file__),'template/user/picture','list.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class PictureDeleteEndHandler(webapp.RequestHandler):
  def post(self):
    try:
      user = users.get_current_user()
      if user is None:
        return self.redirect('/index')
      else:
        logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")

      cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
      picturHandlerePage = self.request.get('picturHandlerePage')

      cookie['picturHandlerePage'] = picturHandlerePage.encode('utf-8')
      cookie['picturHandlerePage']['expires'] = 3600
      print cookie.output()

      email = user.email()
      userData = db.GqlQuery("SELECT * FROM User WHERE email='"+email+"'")
      for user in userData:
        id = user.key().id()

      user = User.get_by_id(long(id))
      pictureIdList =  self.request.POST.getall("pictureid")
      sumBinary = 0
      for pil in pictureIdList:
        picture   = Picture.get_by_id(long(pil))
        sumBinary = sumBinary + len(picture.binary)/1000
        PcaDatas = PictureConnectAlbum.gql("WHERE picture = :1 ORDER BY picture", picture)

        for PcaData in PcaDatas:
          albumid = PcaData.album.key().id()
          albumData = Album.get_by_id(long(albumid))
          cnt = albumData.picture_counter - 1
          albumData.picture_counter = cnt
          albumData.put()

        picture.delete()

      contentPicture = user.contentPicture;
      contentPicture = contentPicture-sumBinary
      user.contentPicture = contentPicture
      user.put()

      return self.redirect('/user/picture/list')
    except:
            self.errorFunc()
  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)