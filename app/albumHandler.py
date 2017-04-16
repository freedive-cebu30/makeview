import cgi
import os
import wsgiref.handlers
import xmlrpclib
import string
import re
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
from model.Album import Album
from model.Sum import Sum
from model.PictureConnectAlbum import PictureConnectAlbum
from django.utils import simplejson
from Cookie import SimpleCookie

FILE_MAX         = 100
PAGE             = 16#albumlist
USER_PICTURE_MAX = 20
DEFPICTUREPAGE   = 16
DEFALBUMPAGE     = 3
BOOKMARKPAGE     = 16
#DOMAIN = "localhost:8084"
PROTOCOLHTTP = "http://"
PROTOCOLHTTPS = "https://"
DOMAIN = "make-view.appspot.com"

class AlbumInsertHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user is None:
        return self.redirect('/index')
    else:
      logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
      loginFlg = 1

    num = random.randint(1, 1000000)
    tooken = num

    cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
    cookie['albumtooken'] = tooken
    cookie['albumtooken']['expires'] = 3600
    print cookie.output()

    params = {'logout_link' : logout_link,
              'loginFlg'    : loginFlg,
              'tooken'      : tooken
              }
    fpath = os.path.join(os.path.dirname(__file__),'template/user/album','insert.html')
    html = template.render(fpath, params)
    self.response.out.write(html)

    return

class AlbumInsertEndHandler(webapp.RequestHandler):
  def post(self):
    try:
      user = users.get_current_user()
      if user is None:
        return self.redirect('/index')
      else:
        logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
        loginFlg = 1

      cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
      if cookie.has_key('albumtooken'):
        tooken = cookie['albumtooken'].value

      cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
      cookie['albumtooken'] = ""
      cookie['albumtooken']['expires'] = 3600
      print cookie.output()
      hiddenToken = self.request.get('tooken')

      if tooken != hiddenToken:
        #return self.redirect('/user/album/list')
        raise
      formList = [
                  'title',
                  'postCode',
                  'address',
                  'station',
                  'busStop',
                  'start',
                  'startPostCode',
                  'startAddress',
                  'time',
                  'tag',
                  'timezone',
                  'season',
                  'longitude',
                  'latitude',
                  'longitude2',
                  'latitude2',
                  'recital'
                  ]
      formData={}
      for list in formList:
        formData[list] = self.request.get(list)
      if len(formData['title']) > 20:
        raise RuntimeError("titleMax error")
      if len(formData['address']) > 40:
        raise RuntimeError("addressMax error")
      if len(formData['recital']) > 140:
        raise RuntimeError("addressMax error")

      searchList = []
      searchList  = self.makeIndex(searchList,formData['title'],0,5)
      searchList  = self.makeIndex(searchList,formData['address'],0,5)
      searchList  = self.makeIndex(searchList,formData['station'],1,10)
      recitalStr  = formData['recital']

      recitalList = []
      trimRecitalStr = self.removeKaigyou(recitalStr)
      recitalList = self.makeIndex(recitalList,trimRecitalStr,0,5)

      pat = re.compile('\[[^\]]+\]')
      taglist = pat.findall(formData['tag'])

      pat2 = re.compile('\[')
      taglist2 = []
      pat3 = re.compile('\]')
      tagStr = ""
      count = len(taglist)

      i = 0
      for tl in taglist:
        i +=1
        st = pat2.sub("",tl)
        taglist2.append(pat3.sub("",st))
        if i == count:
          tagStr += pat3.sub("",st)
        else:
          tagStr += pat3.sub("",st)+","

      counterData = Sum.all()
      sumDatas = []
      keyId = ""
      i = 0
      for cd in counterData:
        i += 1
        sumDatas.append(cd.album_counter)
        keyId = cd.key().id()
      sum_counter = 0
      if i == 0:
        sum_counter = 1
        sum = Sum()
        sum.album_counter = 1
        sum.put()
      else:
        sum_counter = sumDatas[0]+1
        sumData = Sum.get_by_id(long(keyId))
        sumData.album_counter = sum_counter
        sumData.put()

      email = user.email()
      userData = db.GqlQuery("SELECT * FROM User WHERE email='"+email+"'")
      data = Album(picture_counter=0,picture_max=USER_PICTURE_MAX)
      for user in userData:
        id = user.key().id()
      user = User.get_by_id(long(id))
      data.user            = user
      data.title           = formData['title']
      data.post_code       = formData['postCode']
      data.address         = formData['address']
      data.station         = formData['station']
      data.bus_stop        = formData['busStop']
      data.start           = formData['start']
      data.start_post_code = formData['startPostCode']
      data.start_address   = formData['startAddress']
      data.time            = formData['time']
      data.tag_str         = tagStr
      data.tag             = taglist2
      data.search_index    = searchList+taglist2+recitalList
      data.timezone        = int(formData['timezone'])
      data.season          = int(formData['season'])
      data.watch_counter   = 0
      data.recital         = formData['recital']
      data.point           = formData['latitude']+","+formData['longitude']
      data.point2          = formData['latitude2']+","+formData['longitude2']
      data.latitude        = formData['latitude']
      data.longitude       = formData['longitude']

      data.put()

      params = {'logout_link' : logout_link}

      fpath = os.path.join(os.path.dirname(__file__),'template/user/album','insertend.html')
      html = template.render(fpath,'')
      self.response.out.write(html)
    except:
      self.errorFunc()
  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)
  def makeIndex(self, indexList, stringValue, y=0, maxlength=10):
    i = 0
    y += 1
    count = len(stringValue)
    for i in range(count):
      indexList.append(stringValue[i:i+y])
    if y < maxlength:
      indexList = self.makeIndex(indexList,stringValue, y)
    return indexList

  def removeKaigyou(self, recitalStr):
    count = len(recitalStr)
    i = 0
    trimRecitalStr = ""
    st = ""
    for i in range(count):
      st = recitalStr[i:i+1]
      st = string.rstrip(st,'')
      st = string.rstrip(st,'\n')
      st = string.rstrip(st,'\r')
      trimRecitalStr += st
    return trimRecitalStr

class AlbumUpdateHandler(webapp.RequestHandler):
  def post(self):
    try:
      user = users.get_current_user()
      if user is None:
        return self.redirect('/index')
      else:
        logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
        loginFlg = 1

      albumid = self.request.get('albumid')
      datas = Album.get_by_id(long(albumid))
      new_data=''
      for data in datas.tag:
        new_data = new_data+"["+data+"]"
      point     = str(datas.point)
      pointData = point.split(',')
      latitude  = pointData.pop(0)
      longitude = pointData.pop(0)

      point2     = str(datas.point2)

      latitude2  = ""
      longitude2 = ""
      if point2 != "None":
        pointData2 = point2.split(',')
        latitude2  = pointData2.pop(0)
        longitude2 = pointData2.pop(0)

      num = random.randint(1, 1000000)
      tooken = num

      cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
      cookie['albumtooken'] = tooken
      cookie['albumtooken']['expires'] = 3600
      print cookie.output()

      params = {'datas'       : datas,
                'new_data'    : new_data,
                'latitude'    : latitude,
                'longitude'   : longitude,
                'latitude2'   : latitude2,
                'longitude2'  : longitude2,
                'loginFlg'    : loginFlg,
                'logout_link' : logout_link,
                'tooken'      : tooken
                }
      fpath = os.path.join(os.path.dirname(__file__),'template/user/album','update.html')
      html = template.render(fpath,params)
      self.response.out.write(html)
    except:
      self.errorFunc()

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

class AlbumUpdateEndHandler(webapp.RequestHandler):
    def post(self):
      try:
        user = users.get_current_user()
        if user is None:
            return self.redirect('/index')
        else:
          logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
          loginFlg = 1

        cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
        if cookie.has_key('albumtooken'):
          tooken = cookie['albumtooken'].value

        cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
        cookie['albumtooken'] = ""
        cookie['albumtooken']['expires'] = 3600
        print cookie.output()
        hiddenToken = self.request.get('tooken')

        if tooken != hiddenToken:
          #return self.redirect('/user/album/list')
          raise

        formList = [
                    'title',
                    'postCode',
                    'address',
                    'station',
                    'busStop',
                    'start',
                    'startPostCode',
                    'startAddress',
                    'time',
                    'tag',
                    'timezone',
                    'season',
                    'longitude',
                    'latitude',
                    'longitude2',
                    'latitude2',
                    'recital'
                    ]
        formData={}
        for list in formList:
          formData[list] = self.request.get(list)
        if len(formData['title']) > 20:
          raise RuntimeError("titleMax error")
        if len(formData['address']) > 40:
          raise RuntimeError("addressMax error")
        if len(formData['recital']) > 140:
          raise RuntimeError("addressMax error")
        taglist = formData['tag'].split('^[.+]$')

        searchList = []
        searchList  = self.makeIndex(searchList,formData['title'],0,5)
        searchList  = self.makeIndex(searchList,formData['address'],0,5)
        searchList  = self.makeIndex(searchList,formData['station'],1,10)
        recitalStr  = formData['recital']

        recitalList = []
        trimRecitalStr = self.removeKaigyou(recitalStr)
        recitalList = self.makeIndex(recitalList,trimRecitalStr,0,5)

        pat = re.compile('\[[^\]]+\]')
        taglist = pat.findall(formData['tag'])

        pat2 = re.compile('\[')
        taglist2 = []
        pat3 = re.compile('\]')
        tagStr = ""
        count = len(taglist)
        i = 0
        for tl in taglist:
          i +=1
          st = pat2.sub("",tl)
          taglist2.append(pat3.sub("",st))
          if i == count:
            tagStr += pat3.sub("",st)
          else:
            tagStr += pat3.sub("",st)+","

        albumid = self.request.get('albumid')
        data = Album.get_by_id(long(albumid))
        data.title           = formData['title']
        data.post_code       = formData['postCode']
        data.address         = formData['address']
        data.station         = formData['station']
        data.bus_stop        = formData['busStop']
        data.start           = formData['start']
        data.start_post_code = formData['startPostCode']
        data.start_address   = formData['startAddress']
        data.time            = formData['time']
        data.tag_str         = tagStr
        data.tag             = taglist2
        data.search_index    = searchList+taglist2+recitalList
        data.timezone        = int(formData['timezone'])
        data.season          = int(formData['season'])
        data.recital         = formData['recital']
        data.point           = formData['latitude']+","+formData['longitude']
        if formData['latitude2'] !="" and formData['longitude2']!="":
          data.point2          = formData['latitude2']+","+formData['longitude2']
        data.latitude        = formData['latitude']
        data.longitude       = formData['longitude']

        data.put()

        params = {"logout_link" : logout_link }
        fpath = os.path.join(os.path.dirname(__file__),'template/user/album','updateend.html')
        html = template.render(fpath,params)
        self.response.out.write(html)
      except:
        self.errorFunc()

    def errorFunc(self):
      fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
      html = template.render(fpath,'')
      self.response.out.write(html)
    def makeIndex(self, indexList, stringValue, y=0,maxlength=10):
      i = 0
      y += 1
      count = len(stringValue)
      for i in range(count):
        indexList.append(stringValue[i:i+y])
      if y < maxlength:
        indexList = self.makeIndex(indexList,stringValue, y)

      return indexList

    def removeKaigyou(self, recitalStr):
      count = len(recitalStr)
      i = 0
      trimRecitalStr = ""
      st = ""
      for i in range(count):
        st = recitalStr[i:i+1]
        st = string.rstrip(st,'')
        st = string.rstrip(st,'\n')
        st = string.rstrip(st,'\r')
        trimRecitalStr += st

      return trimRecitalStr

class AlbumListHandler(webapp.RequestHandler):
  def get(self):
    try:
      user = users.get_current_user()
      if user is None:
        return self.redirect('/index')
      else:
        logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
        loginFlg = 1

      email = user.email()
      userData = db.GqlQuery("SELECT * FROM User WHERE email='"+email+"'")
      userCount = userData.count()

      if userCount < 1:
        firstUser = User()
        firstUser.name                = ""
        firstUser.nickname            = user.nickname()
        firstUser.email               = user.email()
        #firstUser.age                 = 0
        firstUser.sex                 = 3
        firstUser.post_code           = ""
        firstUser.address             = ""
        firstUser.telFirst            = ""
        firstUser.telSecond           = ""
        firstUser.telThird            = ""
        firstUser.googleAccount       = user
        firstUser.twitterAccount      = ""
        firstUser.delegate            = ""
        firstUser.chargePerson        = ""
        #firstUser.capital             = 0
        firstUser.corporateFlg        = 1
        firstUser.corporate           = ""
        firstUser.recital             = ""
        firstUser.mapflg              = 1
        firstUser.accessFlg           = 0
        firstUser.loginCounter        = 0
        firstUser.contentPicture      = 0
        firstUser.contentPictureLimit = 1000000

        key = firstUser.put()
        userid = key.id()
      else:
        for user in userData:
          userid = user.key().id()

      userData = User.get_by_id(long(userid))
      count = userData.loginCounter
      if count is not None:
        count = count+1
      else:
        count = 1
      userData.loginCounter = count

      if userData.accessFlg == 1:
        return self.redirect('/index')

      cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))

      userAlbumDatas = userData.album_set
      userData.put()

      keyList = list()
      for AlbumData in userAlbumDatas:
        keyList.append(AlbumData.key().id())

      page = self.request.get("page")
      try:
          page = int(page) - 1
      except:
          page = 0
      searchlAbumTitle = self.request.get("searchlAbumTitle")
      clear = self.request.get("clear")
      if clear == "1":
        cookie['searchlAbumTitle'] = ""
        print cookie.output()

      if searchlAbumTitle !="":
        cookie['searchlAbumTitle'] = searchlAbumTitle.encode('utf-8')
        cookie['searchlAbumTitle']['expires'] = 3600
      else:
        if cookie.has_key('searchlAbumTitle'):
          searchlAbumTitle = cookie['searchlAbumTitle'].value.decode('utf-8')

      print cookie.output()
      if searchlAbumTitle == "":
        AlbumDatas = Album.all()
      else:
        AlbumDatas = Album.gql("WHERE search_index =:1", searchlAbumTitle)
      datas = list()
      for AlbumData in AlbumDatas:
        if AlbumData.key().id() in keyList:
          if AlbumData.picture_counter !=0:
            PcaDatas = PictureConnectAlbum.gql("WHERE album = :1 ORDER BY album,order_picture", AlbumData)
            pictureid = 0;
            for PcaData in PcaDatas:
              try:
                PictureDatas = PcaData.picture
                pictureid = int(PictureDatas.key().id())
                if(pictureid != 0):
                  break
              except:
                pictureid=0

            AlbumData.pictureid = pictureid
            datas.append(AlbumData)

            for data in datas:
              if len(data.title) > 7:
                da2 = data.title[0:7]
                da2 +="..."
                data.title = da2

      albumCount = len(datas)
      pagerFlg = 0
      if albumCount > PAGE:
        pagerFlg = 1;

      lastPage = int(math.ceil(float(albumCount)/PAGE))
      if page > lastPage:
        page = lastPage
      paginator = ObjectPaginator(datas,PAGE)
      if page>=paginator.pages:
              page = paginator.pages - 1

      #pager
      #now page picturepage+1
      #last page paginator.pages+1
      page1 = 1
      if page+1 > 2:
        page1 = page+1-1
      elif page+1 > 3:
        page1 = page+1-2
      if page+1 == lastPage+1:
        page1 = page1-3
      elif page == lastPage+1:
        page1 = page1-2

      if page1 < 2:
        page1 = 2

      pages = range(page1-1,lastPage+1)

      params = {
          "datas"            : paginator.get_page(page),
          "pages"            : pages,
          "page"             : page+1,
          "prev"             : page,
          "next"             : page+2,
          "loginFlg"         : loginFlg,
          "pagerFlg"         : pagerFlg,
          "lastpage"         : lastPage,
          "searchlAbumTitle" : searchlAbumTitle,
          "logout_link"      : logout_link
      }

      fpath = os.path.join(os.path.dirname(__file__),'template/user/album','list.html')
      html = template.render(fpath,params)
      self.response.out.write(html)

      return

    except:
      self.errorFunc()

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

class AlbumDeleteAlbumHandler(webapp.RequestHandler):
  def post(self):
    try:
      user = users.get_current_user()
      if user is None:
          return self.redirect('/index')
      else:
        logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
        loginFlg = 1

      data = self.request.get('data')
      dataList  = data.split(":")
      pictureid = dataList.pop(0)
      albumid   = dataList.pop(0)
      picture = Picture.get_by_id(long(pictureid))
      album   = Album.get_by_id(long(albumid))

      datas = PictureConnectAlbum.gql("WHERE album = :1 AND picture= :2", album, picture)
      keyList = list()
      for data in datas:
        id = data.key().id()
      db.run_in_transaction(self.delDecrement,id, album)

      print 1;

      return
    except:
      self.errorFunc()
  def delDecrement(self,id,album):
      pcaData = PictureConnectAlbum.get_by_id(long(id),album)
      pcaData.delete()
      number = int(album.picture_counter)
      album.picture_counter = number-1
      album.put();

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

class AlbumSlideshowHandler(webapp.RequestHandler):
  def get(self):
    try:
      user = users.get_current_user()
      albumid = self.request.get('albumid')
      indexflg = self.request.get('indexflg')

      if indexflg == "1":
        cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
        print cookie
        cookie["searchValue"]=""
        cookie["prefecture"]=""
        cookie["line"]=""
        cookie["station"]=""
        print cookie.output()

      ownFlg = ""

      if user is not None:
        email = user.email()
        userData = db.GqlQuery("SELECT * FROM User WHERE email='"+email+"'")
        for user in userData:
          userid = user.key().id()
        userDatas = User.get_by_id(long(userid))
        userAlbumDatas = userDatas.album_set
        keyList = list()
        for albumData in userAlbumDatas:
          keyList.append(albumData.key().id())

        if int(albumid) in keyList:
          ownFlg = "1"

      AlbumData = Album.get_by_id(long(albumid))
      datas = PictureConnectAlbum.gql("WHERE album = :1 ORDER BY order_picture ASC", AlbumData)
      count = AlbumData.watch_counter
      count = count+1
      AlbumData.watch_counter = count
      AlbumData.put()
      picture = list()
      for data in datas:
        if AlbumData.recital is not None:
          data.picture.recital = AlbumData.recital
        if AlbumData.title is not None:
          data.picture.title = AlbumData.title
        if AlbumData.start is not None:
          data.picture.start = AlbumData.start
        if data.picture_comment is not None:
          data.picture.picture_comment = data.picture_comment
        picture.append(data.picture)

      #################create login#######################
      user = users.get_current_user()
      loginFlg = ""
      user_top_link = ""
      top_link = ""
      logout_link = ""
      if user is not None:
        loginFlg = 1
        logout_link = users.create_logout_url(PROTOCOLHTTPS+DOMAIN+"/index")
      else:
        user_top_link = users.create_login_url(PROTOCOLHTTPS+DOMAIN+"/user")

      params = {"datas"         : picture,
                "album"         : AlbumData,
                "meta_tag"      : AlbumData.tag_str+","+AlbumData.title,
                "user_top_link" : user_top_link,
                "logout_link"   : logout_link,
                "ownFlg"        : ownFlg,
                "loginFlg"      : loginFlg
                }

      fpath = os.path.join(os.path.dirname(__file__),'template/user','slideshow.html')
      html = template.render(fpath,params)
      self.response.out.write(html)
    except:
      self.errorFunc()

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

#Ajax
class AlbumGetAddress(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user is None:
      return self.redirect('/index')
    else:
      logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
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

class AlbumDetailHandler(webapp.RequestHandler):
  def get(self):
    try:
      user = users.get_current_user()
      if user is None:
        return self.redirect('/index')
      else:
        logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
      albumid = self.request.get('albumid')
      datas = Album.get_by_id(long(albumid))
      #################create login#######################
      loginFlg = ""
      user_top_link = ""
      top_link = ""
      if user is not None:
          loginFlg = 1
      else:
          user_top_link = users.create_login_url(PROTOCOLHTTPS+DOMAIN+"/user")

      params = {"datas"         : datas,
                "user_top_link" : user_top_link,
                "loginFlg"      : loginFlg,
                "logout_link"   : logout_link
                }
      fpath = os.path.join(os.path.dirname(__file__),'template/user/album','detail.html')
      html = template.render(fpath,params)
      self.response.out.write(html)

      return
    except:
      self.errorFunc()

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

class AlbumDeleteEndHandler(webapp.RequestHandler):
  def post(self):
    try:
      user = users.get_current_user()
      if user is None:
        return self.redirect('/index')
      else:
        logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
        loginFlg = 1

      counterData = Sum.all()
      sumDatas = []
      keyId = ""
      i = 0
      for cd in counterData:
        i += 1
        sumDatas.append(cd.album_counter)
        keyId = cd.key().id()
      sum_counter = 0
      if i != 0:
        sum_counter = sumDatas[0]-1
        sumData = Sum.get_by_id(long(keyId))
        sumData.album_counter = sum_counter
        sumData.put()

      albumid = self.request.get('albumid')
      album = Album.get_by_id(long(albumid))
      PcaDatas = PictureConnectAlbum.gql("WHERE album = :1 ORDER BY album", album)
      for pcaData in PcaDatas:
        pcaData.delete()

      album.delete()

      #################create login#######################
      user = users.get_current_user()
      loginFlg = ""
      user_top_link = ""
      top_link = ""
      if user:
          loginFlg = 1
      else:
          user_top_link = users.create_login_url(PROTOCOLHTTPS+DOMAIN+"/user")

      params = {
                "user_top_link" : user_top_link,
                "loginFlg"      : loginFlg,
                "logout_link"   : logout_link
                }
      fpath = os.path.join(os.path.dirname(__file__),'template/user/album','deleteend.html')
      html = template.render(fpath,params)
      self.response.out.write(html)

      return
    except:
      self.errorFunc()

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

class AlbumMakeSlideshowHandler(webapp.RequestHandler):
  def get(self):
    try:
      user = users.get_current_user()
      if user is None:
          return self.redirect('/index')
      else:
        logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
        loginFlg = 1

      cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
      #############PICTURE#######################
      picturepage = self.request.get('picturepage')
      zoomFlg     = self.request.get('zoomFlg')
      clear       = self.request.get('clear')
      send        = self.request.get('send')
      if zoomFlg == "" and send != "1":
        if cookie.has_key('zoomFlg'):
          zoomFlg = cookie['zoomFlg'].value

      if zoomFlg == '1':
          cookie['zoomFlg'] = '1'
          cookie['zoomFlg']['expires'] = 3600
      else:
        if cookie.has_key('zoomFlg'):
          cookie['zoomFlg'] = ''

      if clear == "1":
        cookie['picturepage']  = ""
        cookie['picturelabel'] = ""
        cookie['albumpage']    = ""
        cookie['albumtitle']   = ""
        cookie['zoomFlg']      = ""

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
      if picturepage < 0:
        picturepage = 0
      #######if user###################
      email = user.email()
      userData = db.GqlQuery("SELECT * FROM User WHERE email='"+email+"'")
      for user in userData:
        userid = user.key().id()
      userDatas = User.get_by_id(long(userid))

      userPictureDatas = userDatas.picture_set
      keyList = list()
      for PictureData in userPictureDatas:
        keyList.append(PictureData.key().id())

      picturelabel = self.request.get("picturelabel")
      if picturelabel =='':
        if cookie.has_key('picturelabel'):
          picturelabel = cookie['picturelabel'].value.decode('utf-8')
      else:
        cookie['picturelabel'] = picturelabel.encode('utf-8')
        cookie['picturelabel']['expires'] = 3600

      if picturelabel == "":
        PictureDatas = Picture.all()
      else:
        PictureDatas = Picture.gql("WHERE label =:1", picturelabel)
      pictureList = list()
      for PictureData in PictureDatas:
        if PictureData.key().id() in keyList:
          pictureList.append(PictureData)

      picountList = list()
      for picture in pictureList:
        picountList.append(picture)

      pictureLastPage = int(math.ceil(float(len(picountList))/DEFPICTUREPAGE))
      if picturepage > pictureLastPage:
        picturepage = pictureLastPage
      paginator = ObjectPaginator(pictureList,DEFPICTUREPAGE)
      #######if user end###################

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
      try:
        albumpage = int(albumpage) - 1
      except:
          albumpage = 0
      if albumpage < 0:
        albumpage = 0

      #######if user###################
      userAlbumDatas = userDatas.album_set
      keyList = list()
      for AlbumData in userAlbumDatas:
        keyList.append(AlbumData.key().id())

      albumtitle = self.request.get("albumtitle")
      if albumtitle =='':
        if cookie.has_key('albumtitle'):
          albumtitle = cookie['albumtitle'].value.decode('utf-8')
      else:
        cookie['albumtitle'] = albumtitle.encode('utf-8')
        cookie['albumtitle']['expires'] = 3600

      print cookie.output()
      if albumtitle == "":
        AlbumDatas = Album.all()
      else:
        AlbumDatas = Album.gql("WHERE search_index =:1", albumtitle)

      albumList = list()
      for AlbumData in AlbumDatas:
        if AlbumData.key().id() in keyList:
          albumList.append(AlbumData)

      albumpaginator = ObjectPaginator(albumList,DEFALBUMPAGE)
      #######if user end###################
      alcountList = list()
      for data in albumList:
        alcountList.append(data)

      albumLastPage = int(math.ceil(float(len(alcountList))/DEFALBUMPAGE))
      if albumpage > albumLastPage:
        albumpage = albumLastPage

      if albumpage>=albumpaginator.pages:
          albumpage = albumpaginator.pages - 1

      picturePagerFlg = 0
      if len(picountList) > DEFPICTUREPAGE:
        picturePagerFlg = 1;

      albumPagerFlg = 0
      if len(alcountList) > DEFALBUMPAGE:
        albumPagerFlg = 1;

      #pager
      #now page picturepage+1
      #last page paginator.pages+1
      page1 = 1
      if picturepage+1 > 2:
        page1 = picturepage+1-1
      elif picturepage+1 > 3:
        page1 = picturepage+1-2

      if picturepage+1 == pictureLastPage+1:
        page1 = page1-3
      elif picturepage == pictureLastPage+1:
        page1 = page1-2

      if page1 < 2:
        page1 = 2
      #print pictureLastPage
      picturepages = range(page1-1,pictureLastPage+1)

      #pager
      #now page albumpage+1
      #last page albumpaginator.pages+1
      page2 = 1
      if albumpage+1 > 2:
        page2 = albumpage+1-1
      elif albumpage+1 > 3:
        page2 = albumpage+1-2

      if albumpage+1 == albumLastPage+1:
        page2 = page2-3
      elif albumpage == albumLastPage+1:
        page2 = page2-2

      if page2 < 2:
        page2 = 2

      albumpages = range(page2-1,albumpaginator.pages+1)

      params = {
          "datas"           : paginator.get_page(picturepage),
          "picturelabel"    : picturelabel,
          "albumtitle"      : albumtitle,
          "picturepages"    : picturepages,
          "picturepage"     : picturepage+1,
          "picturelastpage" : pictureLastPage,
          "picturePagerFlg" : picturePagerFlg,
          "pictureprev"     : picturepage,
          "picturenext"     : picturepage+2,
          "albumdatas"      : albumpaginator.get_page(albumpage),
          "albumpages"      : albumpages,
          "albumpage"       : albumpage+1,
          "albumlastpage"   : albumLastPage,
          "albumPagerFlg"   : albumPagerFlg,
          "albumprev"       : albumpage,
          "albumnext"       : albumpage+2,
          "loginFlg"        : loginFlg,
          "zoomFlg"         : zoomFlg,
          "logout_link"     : logout_link
      }

      fpath = os.path.join(os.path.dirname(__file__),'template/user/album','makeslideshow.html')
      html = template.render(fpath,params)
      self.response.out.write(html)

      return
    except:
      self.errorFunc()

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

class AlbumAddAlbumHandler(webapp.RequestHandler):
  def post(self):
    try:
      user = users.get_current_user()
      if user is None:
        return self.redirect('/index')
      else:
        logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
        loginFlg = 1

      data = self.request.get('data')
      dataList  = data.split(":")
      pictureid = dataList.pop(0)
      albumid   = dataList.pop(0)
      picture = Picture.get_by_id(long(pictureid))
      album   = Album.get_by_id(long(albumid))
      number = int(album.picture_counter)
      pcagql = PictureConnectAlbum.gql("WHERE picture=:1 AND album=:2",picture,album)

      if pcagql.count() > 0:
        self.response.out.write('2')
      elif number < 20:
        db.run_in_transaction(self.addIncrement,picture,album)
      else:
        self.response.out.write('3')

    except:
      self.errorFunc()
  def addIncrement(self,picture,album):
      pcaData = PictureConnectAlbum(picture=picture,album=album,parent=album)
      pcaData.order_picture = 0
      pcaData.put()
      number = int(album.picture_counter)
      if number < 20:
        album.picture_counter = number+1
        album.put();
        self.response.out.write('1')
      else:
        self.response.out.write('4')
  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

class AlbumOrderpictureHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user is None:
        return self.redirect('/index')
    else:
        logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
        loginFlg = 1
    albumid = self.request.get('albumid')
    zoomFlg = self.request.get('zoomFlg')
    AlbumDatas = Album.get_by_id(long(albumid))
    datas = PictureConnectAlbum.gql("WHERE album = :1 ORDER BY order_picture ASC", AlbumDatas)
    picture = list()
    for data in datas:
      picture.append(data.picture)

    params = {'datas'       : picture,
              'albumid'     : albumid,
              'zoomFlg'     : zoomFlg,
              'logout_link' : logout_link,
              'loginFlg'    : loginFlg
              }
    fpath = os.path.join(os.path.dirname(__file__),'template/user/album','orderpicture.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AlbumOrderpictureEndHandler(webapp.RequestHandler):
  def get(self):
    try:
      user = users.get_current_user()
      if user is None:
          return self.redirect('/index')
      else:
          logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
          loginFlg = 1
      order   = self.request.get('order')
      albumid = self.request.get('albumid')
      AlbumDatas = Album.get_by_id(long(albumid))
      orderList = list()
      orderList = order.split(",");
      i = 0
      for pictureid in orderList:
        if pictureid !='':
          pictureDatas = Picture.get_by_id(long(pictureid))
          datas = PictureConnectAlbum.gql("WHERE album = :1 AND picture = :2", AlbumDatas,pictureDatas)
          for data in datas:
            id = data.key().id()
          pcaData = PictureConnectAlbum.get_by_id(long(id),AlbumDatas)
          pcaData.order_picture = i
          pcaData.put()
          i += 1

      datas = PictureConnectAlbum.gql("WHERE album = :1 ORDER BY order_picture ASC", AlbumDatas)
      pictureList = list()
      for data in datas:
        pictureList.append(data.picture)

      params = {'datas'       : pictureList,
                'albumid'     : albumid,
                'loginFlg'    : loginFlg,
                'logout_link' : logout_link
                }
      fpath = os.path.join(os.path.dirname(__file__),'template/user/album','orderpicture.html')
      html = template.render(fpath,params)
      self.response.out.write(html)

      return
    except:
      self.errorFunc()

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

class AlbumUpdateSlideshowHandler(webapp.RequestHandler):
  def get(self):
    try:
      user = users.get_current_user()
      if user is None:
          return self.redirect('/index')
      else:
          logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
          loginFlg = 1
      albumid = self.request.get('albumid')
      zoomFlg = self.request.get('zoomFlg')
      AlbumData = Album.get_by_id(long(albumid))
      datas = PictureConnectAlbum.gql("WHERE album = :1 ORDER BY order_picture ASC", AlbumData)
      picture = list()
      for data in datas:
        if data.picture_comment is not None:
          data.picture.picture_comment = data.picture_comment
        picture.append(data.picture)

      params = {'datas'       : picture,
                'album'       : AlbumData,
                'albumid'     : albumid,
                'zoomFlg'     : zoomFlg,
                'loginFlg'    : loginFlg,
                'logout_link' : logout_link
                }
      fpath = os.path.join(os.path.dirname(__file__),'template/user/album','updateslideshow.html')
      html = template.render(fpath,params)
      self.response.out.write(html)

      return
    except:
      self.errorFunc()

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

class AlbumUpdateSlideshowEndHandler(webapp.RequestHandler):
  def post(self):
    try:
      user = users.get_current_user()
      if user is None:
          return self.redirect('/index')
      else:
          logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
          loginFlg = 1
      albumid       = self.request.get('albumid')
      AlbumData    = Album.get_by_id(long(albumid))
      pictureIdList = self.request.POST.getall("pictureid")

      for pictureid in pictureIdList:
        if pictureid !='':
          pictureData = Picture.get_by_id(long(pictureid))
          datas = PictureConnectAlbum.gql("WHERE album = :1 AND picture = :2", AlbumData,pictureData)
          for data in datas:
            id = data.key().id()
          pcaData = PictureConnectAlbum.get_by_id(long(id),AlbumData)
          comment = ""
          comment = self.request.get("comment"+pictureid)
          pcaData.picture_comment = comment
          pcaData.put()
      datas = PictureConnectAlbum.gql("WHERE album = :1 ORDER BY order_picture ASC", AlbumData)
      picture = list()
      for data in datas:
        if data.picture_comment is not None:
          data.picture.picture_comment = data.picture_comment
        picture.append(data.picture)

      params = {'datas'       : picture,
                'album'       : AlbumData,
                'albumid'     : albumid,
                'loginFlg'    : loginFlg,
                'logout_link' : logout_link
                }
      fpath = os.path.join(os.path.dirname(__file__),'template/user/album','updateslideshow.html')
      html = template.render(fpath,params)
      self.response.out.write(html)
    except:
      self.errorFunc()

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

class AlbumDeleteSlideshowHandler(webapp.RequestHandler):
  def post(self):
    try:
      user = users.get_current_user()
      if user is None:
        return self.redirect('/index')
      else:
        logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
      data = self.request.get('data')
      albumid       = self.request.get('albumid')
      pictureIdList = self.request.POST.getall("pictureid")
      album   = Album.get_by_id(long(albumid))
      pictureData = ""
      for pictureid in pictureIdList:
        if pictureid !='':
          pictureData = Picture.get_by_id(long(pictureid))
        datas = PictureConnectAlbum.gql("WHERE album = :1 AND picture= :2", album, pictureData)
        keyList = list()
        for data in datas:
          id = data.key().id()
        db.run_in_transaction(self.delDecrement,id, album)

      return self.redirect('/user/album/updateslideshow?albumid='+albumid)

    except:
      self.errorFunc()
  def delDecrement(self,id,album):
      pcaData = PictureConnectAlbum.get_by_id(long(id),album)
      pcaData.delete()
      number = int(album.picture_counter)
      album.picture_counter = number-1
      album.put();

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

class AlbumInsertBookMarkHandler(webapp.RequestHandler):
  def get(self):
    try:
      user = users.get_current_user()
      if user is None:
          return self.redirect('/index')
      else:
          logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
          loginFlg = 1

      albumid = self.request.get('albumid')
      email = user.email()
      gqlUserData = db.GqlQuery("SELECT * FROM User WHERE email='"+email+"'")

      for user in gqlUserData:
        userid = user.key().id()

      userData = User.get_by_id(long(userid))

      newAlbumList = list()
      albumList = userData.albumList

      if albumList is not None:
        for album in albumList:
          newAlbumList.append(album)
      if albumid not in albumList:
        newAlbumList.append(albumid)

      userData.albumList = newAlbumList

      userData.put()

    except:
      self.response.out.write('1')

class AlbumBookMarkHandler(webapp.RequestHandler):
  def get(self):
    try:
      user = users.get_current_user()
      if user is None:
          return self.redirect('/index')
      else:
          logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
          loginFlg = 1

      page = self.request.get("page")
      try:
          page = int(page) - 1
      except:
          page = 0

      email = user.email()
      gqlUserData = db.GqlQuery("SELECT * FROM User WHERE email='"+email+"'")

      for user in gqlUserData:
        userid = user.key().id()

      userData = User.get_by_id(long(userid))
      albumIdList = list()
      albumIdList = userData.albumList

      albumList = list()
      if albumIdList is not None:
        for id in albumIdList:
          AlbumData = Album.get_by_id(long(id))
          albumList.append(AlbumData)
      datas = list()
      for AlbumData in albumList:
        if AlbumData.picture_counter !=0:
            PcaDatas = PictureConnectAlbum.gql("WHERE album = :1 ORDER BY album,order_picture", AlbumData)
            pictureid = 0;
            for PcaData in PcaDatas:
              try:
                PictureDatas = PcaData.picture
                pictureid = int(PictureDatas.key().id())
                if(pictureid != 0):
                  break
              except:
                pictureid=0

            AlbumData.pictureid = pictureid
            datas.append(AlbumData)

      albumCount = len(datas)
      pagerFlg = 0
      if albumCount > BOOKMARKPAGE:
        pagerFlg = 1;

      lastPage = int(math.ceil(float(albumCount)/BOOKMARKPAGE))
      if page > lastPage:
        page = lastPage
      paginator = ObjectPaginator(albumList,BOOKMARKPAGE)
      if page>=paginator.pages:
              page = paginator.pages - 1

      #pager
      #now page picturepage+1
      #last page paginator.pages+1
      page1 = 1
      if page+1 > 2:
        page1 = page+1-1
      elif page+1 > 3:
        page1 = page+1-2
      if page+1 == lastPage+1:
        page1 = page1-3
      elif page == lastPage+1:
        page1 = page1-2

      if page1 < 2:
        page1 = 2

      pages = range(page1-1,lastPage+1)

      params = {
          "datas"            : paginator.get_page(page),
          "pages"            : pages,
          "page"             : page+1,
          "prev"             : page,
          "next"             : page+2,
          "loginFlg"         : loginFlg,
          "pagerFlg"         : pagerFlg,
          "lastpage"         : lastPage,
          "logout_link"      : logout_link
      }

      fpath = os.path.join(os.path.dirname(__file__),'template/user/album','bookmark.html')
      html = template.render(fpath,params)
      self.response.out.write(html)

      return
    except:
      self.errorFunc()

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

