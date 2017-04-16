import cgi
import os
import wsgiref.handlers
import xmlrpclib
import string
import re
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
PAGE             = 15
USER_PICTURE_MAX = 20
PICTUREPAGE      = 15
ALBUMPAGE        = 4

class AdminAlbumInsertHandler(webapp.RequestHandler):
  def post(self):
    admin = users.is_current_user_admin()
    if not admin:
        return self.redirect('/admin/index')
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','insert.html')
    html = template.render(fpath,'')
    self.response.out.write(html)
  def get(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','insert.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

    return

class AdminAlbumInsertEndHandler(webapp.RequestHandler):
  def post(self):
    #try:
      admin = users.is_current_user_admin()
      if not admin:
          return self.redirect('/admin/index')
      user = users.get_current_user()
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
      data.latitude        = formData['latitude']
      data.longitude       = formData['longitude']

      data.put()

      fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','insertend.html')
      html = template.render(fpath,'')
      self.response.out.write(html)
#    except:
#      self.errorFunc()
  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/admin','error.html')
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

#Ajax
class AdminAlbumGetAddress(webapp.RequestHandler):
  def get(self):
    admin = users.is_current_user_admin()
    if not admin:
      return self.redirect('/admin/index')
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

class AdminAlbumUpdateHandler(webapp.RequestHandler):
  def post(self):
    admin = users.is_current_user_admin()
    if not admin:
        return self.redirect('/admin/index')
    albumid = self.request.get('albumid')
    datas = Album.get_by_id(long(albumid))
    new_data=''
    for data in datas.tag:
      new_data = new_data+"["+data+"]"
    point     = str(datas.point)
    pointData = point.split(',')
    latitude  = pointData.pop(0)
    longitude = pointData.pop(0)

    params = {'datas':datas,
              'new_data':new_data,
              'latitude':latitude,
              'longitude':longitude,
              }
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','update.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

class AdminAlbumUpdateEndHandler(webapp.RequestHandler):

    def post(self):
      try:
        admin = users.is_current_user_admin()
        if not admin:
            return self.redirect('/admin/index')
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
        data.latitude        = formData['latitude']
        data.longitude       = formData['longitude']

        data.put()

        fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','updateend.html')
        html = template.render(fpath,'')
        self.response.out.write(html)
      except:
        self.errorFunc()

    def errorFunc(self):
      fpath = os.path.join(os.path.dirname(__file__),'template/admin','error.html')
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


class AdminAlbumListHandler(webapp.RequestHandler):
  def get(self):
    admin = users.is_current_user_admin()
    if not admin:
        return self.redirect('/admin/index')
    page = self.request.get('page')
    try:
        page = int(page) - 1
    except:
        page = 0
    searchTitle = self.request.get("searchTitle")
    if searchTitle == "":
      AlbumDatas = Album.all()
    else:
      AlbumDatas = Album.gql("WHERE search_index =:1", searchTitle)
    datas = list()
    for AlbumData in AlbumDatas:
      PcaDatas = PictureConnectAlbum.gql("WHERE album = :1 ORDER BY album,order_picture", AlbumData)
      pictureid = 0;
      for PcaData in PcaDatas:
        PictureDatas = PcaData.picture
        pictureid = int(PictureDatas.key().id())
        if(pictureid != 0):
          break

      AlbumData.pictureid = pictureid
      datas.append(AlbumData)

    paginator = ObjectPaginator(datas,PAGE)
    if page>=paginator.pages:
            page = paginator.pages - 1
    params = {
        "searchTitle" : searchTitle,
        "datas"       : paginator.get_page(page),
        "pages"       : range(1,paginator.pages+1),
        "page"        : page+1
    }
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','list.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminAlbumDetailHandler(webapp.RequestHandler):
  def get(self):
    admin = users.is_current_user_admin()
    if not admin:
        return self.redirect('/admin/index')
    albumid = self.request.get('albumid')
    datas = Album.get_by_id(long(albumid))
    params = {'datas':datas}
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','detail.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminAlbumDeleteConfirmHandler(webapp.RequestHandler):
  def post(self):
    admin = users.is_current_user_admin()
    if not admin:
        return self.redirect('/admin/index')
    albumid = self.request.get('albumid')
    datas = Album.get_by_id(long(albumid))
    params = {'datas':datas}
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','deleteconfirm.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminAlbumDeleteEndHandler(webapp.RequestHandler):
  def post(self):
    admin = users.is_current_user_admin()
    if not admin:
        return self.redirect('/admin/index')
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
    data = Album.get_by_id(long(albumid))
    data.delete()
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','deleteend.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

    return

class AdminAlbumAddAlbumHandler(webapp.RequestHandler):
  def post(self):
    try:
      admin = users.is_current_user_admin()
      if not admin:
          return self.redirect('/admin/index')
      data = self.request.get('data')
      dataList  = data.split(":")
      pictureid = dataList.pop(0)
      albumid   = dataList.pop(0)
      picture = Picture.get_by_id(long(pictureid))
      album   = Album.get_by_id(long(albumid))
      number = int(album.picture_counter)
      pcagql = PictureConnectAlbum.gql("WHERE picture=:1 AND album=:2",picture,album)

      if pcagql.count() > 0:
        #json = simplejson.dumps(datas, ensure_ascii=False)
        #self.response.content_type = 'application/json'
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
    fpath = os.path.join(os.path.dirname(__file__),'template/admin','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

class AdminAlbumDeleteAlbumHandler(webapp.RequestHandler):
  def post(self):
    try:
      admin = users.is_current_user_admin()
      if not admin:
          return self.redirect('/admin/index')
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

      self.response.out.write('1')

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
    fpath = os.path.join(os.path.dirname(__file__),'template/admin','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

class AdminAlbumAllpictureHandler(webapp.RequestHandler):
  def get(self):
    admin = users.is_current_user_admin()
    if not admin:
        return self.redirect('/admin/index')

    albumid = self.request.get('albumid')
    zoomFlg = self.request.get('zoomFlg')

    AlbumDatas = Album.get_by_id(long(albumid))
    datas = PictureConnectAlbum.gql("WHERE album = :1", AlbumDatas)
    picture = list()
    for data in datas:
      picture.append(data.picture)

    params = {'datas'   :picture,
              'zoomFlg' :zoomFlg,
              'albumid' :albumid
              }
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','allpicture.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminAlbumOrderpictureHandler(webapp.RequestHandler):
  def get(self):
    admin = users.is_current_user_admin()
    if not admin:
        return self.redirect('/admin/index')
    albumid = self.request.get('albumid')
    AlbumDatas = Album.get_by_id(long(albumid))
    datas = PictureConnectAlbum.gql("WHERE album = :1 ORDER BY order_picture ASC", AlbumDatas)
    picture = list()
    for data in datas:
      picture.append(data.picture)

    params = {'datas':picture,
              'albumid':albumid
              }
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','orderpicture.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminAlbumOrderpictureEndHandler(webapp.RequestHandler):
  def post(self):
    admin = users.is_current_user_admin()
    if not admin:
        return self.redirect('/admin/index')
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

    params = {'datas':pictureList,
              'albumid':albumid
              }
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','orderpicture.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminAlbumSlideshowHandler(webapp.RequestHandler):
  def get(self):
    admin = users.is_current_user_admin()
    if not admin:
        return self.redirect('/admin/index')
    albumid = self.request.get('albumid')
    AlbumData = Album.get_by_id(long(albumid))
    datas = PictureConnectAlbum.gql("WHERE album = :1 ORDER BY order_picture ASC", AlbumData)
    picture = list()
    for data in datas:
      if AlbumData.recital is not None:
        data.picture.recital = AlbumData.recital
      if data.picture_comment is not None:
        data.picture.picture_comment = data.picture_comment
      picture.append(data.picture)

    params = {'datas' : picture,
              'album' : AlbumData
              }
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','slideshow.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return
class AdminAlbumMakeSlideshowHandler(webapp.RequestHandler):
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
    #######if user###################
#    userid = user.key.id()
#    datas = User.get_by_id(long(userid))
#    params = {'datas':datas}
#
#    paginator = ObjectPaginator(datas.picture_set,PICTUREPAGE)
    #######if user end###################
    #######if admin###################
    pictureDatas = Picture.all()
    paginator = ObjectPaginator(pictureDatas,PICTUREPAGE)
    #######if admin end###################
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
    #######if user###################
    #albumpaginator = ObjectPaginator(datas.album_set,ALBUMPICTURE)
    #######if user end###################
    #######if admin###################
    albumDatas = Album.all()
    albumpaginator = ObjectPaginator(albumDatas,ALBUMPAGE)
    #######if admin end###################
    if albumpage>=albumpaginator.pages:
        albumpage = albumpaginator.pages - 1

    params = {
        "datas"        : paginator.get_page(picturepage),
        "picturepages" : range(1,paginator.pages+1),
        "picturepage"  : picturepage+1,
        #"userid"       : datas,
        "albumdatas"   : albumpaginator.get_page(albumpage),
        "albumpages"   : range(1,albumpaginator.pages+1),
        "albumpage"    : albumpage+1
    }

    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','makeslideshow.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminAlbumSlideshowAlbumListHandler(webapp.RequestHandler):
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
    #######if user###################
#    userid = user.key.id()
#    datas = User.get_by_id(long(userid))
#    params = {'datas':datas}
#
#    paginator = ObjectPaginator(datas.picture_set,PICTUREPAGE)
    #######if user end###################
    #######if admin###################
    pictureDatas = Picture.all()
    paginator = ObjectPaginator(pictureDatas,PICTUREPAGE)
    #######if admin end###################
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

    #######if user###################
    #albumpaginator = ObjectPaginator(datas.album_set,ALBUMPICTURE)
    #######if user end###################
    #######if admin###################
    albumDatas = Album.all()
    albumpaginator = ObjectPaginator(albumDatas,ALBUMPAGE)
    #######if admin end###################

    if albumpage>=albumpaginator.pages:
        albumpage = albumpaginator.pages - 1

    params = {
        "datas"        : paginator.get_page(picturepage),
        "picturepages" : range(1,paginator.pages+1),
        "picturepage"  : picturepage+1,
        #"userid"       : datas,
        "albumdatas"   : albumpaginator.get_page(albumpage),
        "albumpages"   : range(1,albumpaginator.pages+1),
        "albumpage"    : albumpage+1
    }

    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','makeslideshow.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminAlbumUpdateSlideshowHandler(webapp.RequestHandler):
  def get(self):
    admin = users.is_current_user_admin()
    if not admin:
        return self.redirect('/admin/index')
    albumid = self.request.get('albumid')
    zoomFlg = self.request.get('zoomFlg')
    AlbumData = Album.get_by_id(long(albumid))
    datas = PictureConnectAlbum.gql("WHERE album = :1 ORDER BY order_picture ASC", AlbumData)
    picture = list()
    for data in datas:
      if data.picture_comment is not None:
        data.picture.picture_comment = data.picture_comment
      picture.append(data.picture)

    params = {'datas'   : picture,
              'album'   : AlbumData,
              'albumid' : albumid,
              'zoomFlg' : zoomFlg
              }
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','updateslideshow.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminAlbumUpdateSlideshowEndHandler(webapp.RequestHandler):
  def post(self):
    admin = users.is_current_user_admin()
    if not admin:
        return self.redirect('/admin/index')
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

    params = {'datas'   : picture,
              'album'   : AlbumData,
              'albumid' : albumid
              }
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/album','updateslideshow.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

class AdminAlbumDeleteSlideshowHandler(webapp.RequestHandler):
  def post(self):
    try:
      admin = users.is_current_user_admin()
      if not admin:
          return self.redirect('/admin/index')
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

      return self.redirect('/admin/album/updateslideshow?albumid='+albumid)

    except:
      self.errorFunc()
  def delDecrement(self,id,album):
      pcaData = PictureConnectAlbum.get_by_id(long(id),album)
      pcaData.delete()
      number = int(album.picture_counter)
      album.picture_counter = number-1
      album.put();

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/admin','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)