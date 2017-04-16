import cgi
import os
import operator
import wsgiref.handlers
import datetime
import md5
import math
from django.core.paginator import ObjectPaginator, InvalidPage
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from datetime import *
from model.Picture import Picture
from model.User import User
from model.Album import Album
from model.Prefecture import Prefecture
from model.StationLine import StationLine
from model.PictureConnectAlbum import PictureConnectAlbum
from django.utils import simplejson
from Cookie import SimpleCookie

FILE_MAX = 100
PAGE     = 16
USER_PICTURE_MAX = 20
#DOMAIN = "localhost:8084"
PROTOCOLHTTP = "http://"
PROTOCOLHTTPS = "https://"
DOMAIN = "make-view.appspot.com"

class indexHandler(webapp.RequestHandler):
  def get(self):
    try:
      formList = [
                    'searchValue',
                    'prefecture',
                    'line',
                    'station',
                    'category',
                    'hicategory',
                    'searchflg'

                    ]
      formData={}
      cnt = 0
      cateFlg = 0
      noneFlg = 0
      searchFlg = 0
      stationFlg = 0
      for roopList in formList:
        if self.request.get(roopList) !="":
          cnt += 1
        formData[roopList] = self.request.get(roopList)

      if formData["category"] =="":
        if formData["hicategory"] != "":
          formData["category"] = formData["hicategory"]

      #Defaulut
      todayTime = str(date.today())
      yesterdayTime = date.today()-timedelta(1)
      AlbumDatas = list()

      if formData["searchValue"] == "" and formData["prefecture"] == "" and formData["line"] == "" and formData["station"] == "":
        #if popular
        #gqlAlbumDatas = Album.gql("WHERE updateDate <= :1 AND updateDate > :2",todayTime,yesterdayTime)
        gqlAlbumDatas = Album.gql("ORDER BY updateDate")


      for AlbumData in gqlAlbumDatas:
        AlbumDatas.append(AlbumData)

      if formData["category"] != "" or formData["category"] == "populer":
        filterDatas = list()
        if formData["category"] =="today":
          for data in AlbumDatas:
            strTime = ""
            strTime = str(data.updateDate)
            if strTime[0:10] == todayTime:
              filterDatas.append(data)
        if formData["category"] =="spring":
          for data in AlbumDatas:
            if data.season == 2:
              filterDatas.append(data)
        elif formData["category"] =="summer":
          for data in AlbumDatas:
            if data.season == 3:
              filterDatas.append(data)
        elif formData["category"] =="fall":
          for data in AlbumDatas:
            if data.season == 4:
              filterDatas.append(data)
        elif formData["category"] =="winter":
          for data in AlbumDatas:
            if data.season == 5:
              filterDatas.append(data)
        elif formData["category"] =="recentPopuler":
          kako = date.today()-timedelta(30)
          for data in AlbumDatas:
            if data.updateDate > kako:
              filterDatas.append(data)
        AlbumDatas = list()
        AlbumDatas = filterDatas
      datas = list()
      for AlbumData in AlbumDatas:
        if AlbumData.user.name is not None:
          if AlbumData.user.name !="":
            AlbumData.user.nickname = AlbumData.user.name
        if AlbumData.picture_counter !=0:
          PcaDatas = PictureConnectAlbum.gql("WHERE album = :1 ORDER BY album", AlbumData)
          pictureid = 0;
          for PcaData in PcaDatas:
            try:
              PictureDatas = PcaData.picture
              pictureid = int(PictureDatas.key().id())
              if(pictureid != 0):
                break
            except:
              pictureid=0
          if pictureid != 0:
            AlbumData.pictureid = pictureid
            datas.append(AlbumData)
            strList = list()
            for data in datas:
              if len(data.recital) > 22:
                da = data.recital[0:22]
                da +="..."
                data.subrecital = da
              if len(data.title) > 8:
                da2 = data.title[0:8]
                da2 +="..."
                data.subtitle = da2

      datas.sort(key=operator.attrgetter('watch_counter'))
      datas.reverse()

      tenDatas = list()

      i = 0
      if formData["searchflg"] !="1":
        fetchnum = 10
      else:
        fetchnum = 20
      for data in datas:
        tenDatas.append(data)
        i += 1
        if i == fetchnum:
          break;

      ################selext box######################
      PreDatas     = Prefecture.all()
      prelist      = list()
      lineDatas    = list()
      StationDatas = list()
      for pd in PreDatas:
        prelist.append(pd)
      prelist.sort(key=operator.attrgetter("prefecture_number"))
      if formData["prefecture"] !="":
        lineDatas    = self.createLine(formData["prefecture"])

      if formData["line"] !="":
        StationDatas = self.createStation(formData["line"])
      #################create login#######################
      user = users.get_current_user()
      loginFlg      = ""
      user_top_link = ""
      logout_link   = ""
      if user is not None:
          loginFlg = 1
          logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
      else:
          user_top_link = users.create_login_url(PROTOCOLHTTPS+DOMAIN+"/user")
      #################create map#######################
      prefectureData = Prefecture.gql("WHERE prefecture_number = :1 order by prefecture_number", 26)

      for pd in prefectureData:
        if pd.prefecture_number != 1:
          if len(pd.prefecture_name) == 3:
            prefecture = pd.prefecture_name[0:2]
          if len(pd.prefecture_name)== 4:
            prefecture = pd.prefecture_name[0:3]

      gqlAlbumDatas = Album.gql("WHERE search_index =:1 limit 0, 100", prefecture)
      sortList = list()
      for AlbumData in gqlAlbumDatas:
        try:
          if AlbumData.picture_counter > 0:
            sortList.append(AlbumData)
        except:
          continue
      sortList.sort(key=operator.attrgetter('watch_counter'))

      AlbumDatas = list()
      AlbumDatas2 = list()
      for AlbumData in sortList:
        if AlbumData.latitude is not None and AlbumData.longitude is not None:
          AlbumDatas2.append(AlbumData)

      params = {
          "datas"         : tenDatas,
          "category"      : formData["category"],
          "searchValue"   : formData["searchValue"],
          "prefecture"    : formData["prefecture"],
          "line"          : formData["line"],
          "station"       : formData["station"],
          "hicategory"    : formData["hicategory"],
          "searchflg"     : formData["searchflg"],
          "AlbumDatas"    : AlbumDatas2,
          "PreDatas"      : prelist,
          "lineDatas"     : lineDatas,
          "user_top_link" : user_top_link,
          "logout_link"   : logout_link,
          "loginFlg"      : loginFlg,
          "StationDatas"  : StationDatas
      }

      fpath = os.path.join(os.path.dirname(__file__),'template/user','index.html')
      html = template.render(fpath,params)
      self.response.out.write(html)
    except:
      self.errorFunc()

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

  def createLine(self,prefecture):

    prefectureid = ""
    preGql = Prefecture.gql("WHERE prefecture_name=:1 ",prefecture)
    for pg in preGql:
      prefectureid = pg.key().id()
    if prefectureid == "":
      return

    datas = Prefecture.get_by_id(long(prefectureid))
    staLine = list()
    staLine = datas.stationline_set
    sortList = list()
    for sortData in staLine:
      sortList.append(sortData)
    sortList.sort(key=operator.attrgetter('station_line_name'))
    lineList = list()
    for sl in sortList:
      lineList.append(sl.station_line_name)

    return lineList

  def createStation(self,line):

    stationlineid=""
    staGql = StationLine.gql("WHERE station_line_name=:1 ",line)
    for st in staGql:
      stationlineid = st.key().id()
    if stationlineid =="":
      return
    station = list()
    datas = StationLine.get_by_id(long(stationlineid))
    station = datas.station_set
    sortList = list()
    for sortData in station:
      sortList.append(sortData)
    sortList.sort(key=operator.attrgetter('station_name'))

    lineList = list()
    for st in sortList:
      lineList.append(st.station_name)

    return lineList

class indexSearch(webapp.RequestHandler):
  def get(self):
    try:
      user = users.get_current_user()
      formList = [
                    'searchValue',
                    'prefecture',
                    'line',
                    'station',
                    'category',
                    'hicategory',
                    'searchflg'

                    ]
      formData={}
      cnt = 0
      cateFlg = 0
      noneFlg = 0
      searchFlg = 0
      stationFlg = 0
      for roopList in formList:
        if self.request.get(roopList) !="":
          cnt += 1
        formData[roopList] = self.request.get(roopList)

      if formData["category"] =="":
        if formData["hicategory"] != "":
          formData["category"] = formData["hicategory"]

      cookie = SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
      if formData["searchflg"] == "1":
        cookie["searchValue"]=""
        cookie["prefecture"]=""
        cookie["line"]=""
        cookie["station"]=""

      if formData["searchValue"] != "":
        cookie["searchValue"] = formData["searchValue"].encode('utf-8')
        cookie['searchValue']['expires'] = 3600
      else:
        if cookie.has_key("searchValue"):
          formData["searchValue"] = cookie["searchValue"].value.decode('utf-8')
      if formData["prefecture"] != "":
        cookie["prefecture"] = formData["prefecture"].encode('utf-8')
        cookie["prefecture"]["expires"] = 3600
      else:
        if cookie.has_key("prefecture"):
          formData["prefecture"] = cookie["prefecture"].value.decode('utf-8')
      if formData["line"] != "":
        cookie["line"] = formData["line"].encode('utf-8')
        cookie["line"]["expires"] = 3600
      else:
        if cookie.has_key("line"):
          formData["line"] = cookie["line"].value.decode('utf-8')
      if formData["station"] != "":
        cookie["station"] = formData["station"].encode('utf-8')
        cookie["station"]["expires"] = 3600
      else:
        if cookie.has_key("station"):
          formData["station"] = cookie["station"].value.decode('utf-8')

      print cookie.output()
      #Defaulut
      todayTime = str(date.today())
      yesterdayTime = date.today()-timedelta(1)
      AlbumDatas = list()

      if formData["searchValue"] == "" and formData["prefecture"] == "" and formData["line"] == "" and formData["station"] == "":
         return self.redirect('/index')
      else:
        validataKey = list()
        searchlist = list()

        if formData["searchValue"] != "":
          searchlist2 = formData['searchValue'].split(' ')
          for sc in searchlist2:
            if sc!='':
              searchlist.append(sc)
        if formData["prefecture"] !="":
          prefectureData = Prefecture.gql("WHERE prefecture_name = :1", formData["prefecture"])
          for pd in prefectureData:
            if pd.prefecture_number != 1:
              if len(pd.prefecture_name) == 3:
                prefecture = pd.prefecture_name[0:2]
              if len(pd.prefecture_name)== 4:
                prefecture = pd.prefecture_name[0:3]

          searchlist.append(prefecture)
        if formData["line"] !="" and formData["station"] =="":
          searchlist.append(formData["line"])
        if formData["station"] !="":
          searchlist.append(formData["station"])
        cnt = len(searchlist)
        if cnt == 1:
          gqlAlbumDatas = Album.gql("WHERE search_index =:1", searchlist[0])
        else:
          i = 0
          searchVal = ""
          sqlString = ""
          slList = list()
          for sl in searchlist:
            i+=1
            if i==1:
              sqlString = "search_index =:"+str(i)
            else:
              sqlString += " AND search_index =:"+str(i)
            slList.append(sl)

          if cnt == 2:
            gqlAlbumDatas = Album.gql("WHERE "+sqlString, slList[0],slList[1])
          elif cnt == 3:
            gqlAlbumDatas = Album.gql("WHERE "+sqlString, slList[0],slList[1],slList[2])
          elif cnt == 4:
            gqlAlbumDatas = Album.gql("WHERE "+sqlString, slList[0],slList[1],slList[2],slList[3])
          elif cnt == 5:
            gqlAlbumDatas = Album.gql("WHERE "+sqlString, slList[0],slList[1],slList[2],slList[3],slList[4])
          elif cnt == 6:
            gqlAlbumDatas = Album.gql("WHERE "+sqlString, slList[0],slList[1],slList[2],slList[3],slList[4],slList[5])
          elif cnt == 7:
            gqlAlbumDatas = Album.gql("WHERE "+sqlString, slList[0],slList[1],slList[2],slList[3],slList[4],slList[5],slList[6])
          elif cnt == 8:
            gqlAlbumDatas = Album.gql("WHERE "+sqlString, slList[0],slList[1],slList[2],slList[3],slList[4],slList[5],slList[6],slList[7])
          elif cnt >= 9:
            gqlAlbumDatas = Album.gql("WHERE "+sqlString, slList[0],slList[1],slList[2],slList[3],slList[4],slList[5],slList[6],slList[7],slList[8])
          elif cnt >= 10:
            gqlAlbumDatas = Album.gql("WHERE "+sqlString, slList[0],slList[1],slList[2],slList[3],slList[4],slList[5],slList[6],slList[7],slList[8],slList[9])

      for AlbumData in gqlAlbumDatas:
        AlbumDatas.append(AlbumData)

      if formData["category"] != "" or formData["category"] == "populer":
        filterDatas = list()
        if formData["category"] =="today":
          for data in AlbumDatas:
            strTime = ""
            strTime = str(data.updateDate)
            if strTime[0:10] == todayTime:
              filterDatas.append(data)
        if formData["category"] =="spring":
          for data in AlbumDatas:
            if data.season == 2:
              filterDatas.append(data)
        elif formData["category"] =="summer":
          for data in AlbumDatas:
            if data.season == 3:
              filterDatas.append(data)
        elif formData["category"] =="fall":
          for data in AlbumDatas:
            if data.season == 4:
              filterDatas.append(data)
        elif formData["category"] =="winter":
          for data in AlbumDatas:
            if data.season == 5:
              filterDatas.append(data)
        elif formData["category"] =="recentPopuler":
          kako = date.today()-timedelta(30)
          for data in AlbumDatas:
            if data.updateDate > kako:
              filterDatas.append(data)
        AlbumDatas = list()
        AlbumDatas = filterDatas
      datas = list()
      for AlbumData in AlbumDatas:
        if AlbumData.user.name is not None:
          if AlbumData.user.name !="":
            AlbumData.user.nickname = AlbumData.user.name
        if AlbumData.picture_counter !=0:
          PcaDatas = PictureConnectAlbum.gql("WHERE album = :1 ORDER BY album", AlbumData)
          pictureid = 0;
          for PcaData in PcaDatas:
            try:
              PictureDatas = PcaData.picture
              pictureid = int(PictureDatas.key().id())
              if(pictureid != 0):
                break
            except:
              pictureid=0
          if pictureid != 0:
            AlbumData.pictureid = pictureid
            datas.append(AlbumData)
            strList = list()
            for data in datas:
              if len(data.recital) > 22:
                da = data.recital[0:22]
                da +="..."
                data.subrecital = da
              if len(data.title) > 8:
                da2 = data.title[0:8]
                da2 +="..."
                data.subtitle = da2

      datas.sort(key=operator.attrgetter('watch_counter'))
      datas.reverse()

      page = self.request.get("page")
      try:
          page = int(page) - 1
      except:
          page = 0

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
      if user is not None:
          loginFlg = 1

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

      ################selext box######################
      PreDatas     = Prefecture.all()
      prelist      = list()
      lineDatas    = list()
      StationDatas = list()
      for pd in PreDatas:
        prelist.append(pd)
      prelist.sort(key=operator.attrgetter("prefecture_number"))
      if formData["prefecture"] !="":
        lineDatas    = self.createLine(formData["prefecture"])

      if formData["line"] !="":
        StationDatas = self.createStation(formData["line"])
      #################create login#######################
      user = users.get_current_user()
      loginFlg      = ""
      user_top_link = ""
      logout_link   = ""
      if user is not None:
          loginFlg = 1
          logout_link = users.create_logout_url(PROTOCOLHTTP+DOMAIN+"/index")
      else:
          user_top_link = users.create_login_url(PROTOCOLHTTPS+DOMAIN+"/user")
      #################create map#######################
      prefectureData = Prefecture.gql("WHERE prefecture_number = :1 order by prefecture_number", 26)

      for pd in prefectureData:
        if pd.prefecture_number != 1:
          if len(pd.prefecture_name) == 3:
            prefecture = pd.prefecture_name[0:2]
          if len(pd.prefecture_name)== 4:
            prefecture = pd.prefecture_name[0:3]

      gqlAlbumDatas = Album.gql("WHERE search_index =:1 limit 0, 100", prefecture)
      sortList = list()
      for AlbumData in gqlAlbumDatas:
        try:
          if AlbumData.picture_counter > 0:
            sortList.append(AlbumData)
        except:
          continue
      sortList.sort(key=operator.attrgetter('watch_counter'))

      AlbumDatas = list()
      AlbumDatas2 = list()
      for AlbumData in sortList:
        if AlbumData.latitude is not None and AlbumData.longitude is not None:
          AlbumDatas2.append(AlbumData)

      params = {
          "datas"         : paginator.get_page(page),
          "pages"         : pages,
          "page"          : page+1,
          "prev"          : page,
          "next"          : page+2,
          "pagerFlg"      : pagerFlg,
          "lastpage"      : lastPage,
          "category"      : formData["category"],
          "searchValue"   : formData["searchValue"],
          "prefecture"    : formData["prefecture"],
          "line"          : formData["line"],
          "station"       : formData["station"],
          "hicategory"    : formData["hicategory"],
          "searchflg"     : formData["searchflg"],
          "AlbumDatas"    : AlbumDatas2,
          "PreDatas"      : prelist,
          "lineDatas"     : lineDatas,
          "user_top_link" : user_top_link,
          "logout_link"   : logout_link,
          "loginFlg"      : loginFlg,
          "StationDatas"  : StationDatas
      }

      fpath = os.path.join(os.path.dirname(__file__),'template/user','indexsearch.html')
      html = template.render(fpath,params)
      self.response.out.write(html)
    except:
      self.errorFunc()

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/user','error.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

  def createLine(self,prefecture):

    prefectureid = ""
    preGql = Prefecture.gql("WHERE prefecture_name=:1 ",prefecture)
    for pg in preGql:
      prefectureid = pg.key().id()
    if prefectureid == "":
      return

    datas = Prefecture.get_by_id(long(prefectureid))
    staLine = list()
    staLine = datas.stationline_set
    sortList = list()
    for sortData in staLine:
      sortList.append(sortData)
    sortList.sort(key=operator.attrgetter('station_line_name'))
    lineList = list()
    for sl in sortList:
      lineList.append(sl.station_line_name)

    return lineList

  def createStation(self,line):

    stationlineid=""
    staGql = StationLine.gql("WHERE station_line_name=:1 ",line)
    for st in staGql:
      stationlineid = st.key().id()
    if stationlineid =="":
      return
    station = list()
    datas = StationLine.get_by_id(long(stationlineid))
    station = datas.station_set
    sortList = list()
    for sortData in station:
      sortList.append(sortData)
    sortList.sort(key=operator.attrgetter('station_name'))

    lineList = list()
    for st in sortList:
      lineList.append(st.station_name)

    return lineList

class indexSearchLine(webapp.RequestHandler):
  def get(self):
    prefecture = self.request.get('prefecture')
    #preGql = Prefecture.gql("WHERE prefecture_number=:1 ",int(prefecture))
    preGql = Prefecture.gql("WHERE prefecture_name=:1 ",prefecture)
    prefectureid = "";
    for pg in preGql:
      prefectureid = pg.key().id()
    datas = Prefecture.get_by_id(long(prefectureid))
    staLine = datas.stationline_set
    sortList = list()
    for sortData in staLine:
      sortList.append(sortData)
    sortList.sort(key=operator.attrgetter('station_line_name'))
    lineList = list()
    for sl in sortList:
      lineList.append(sl.station_line_name)
  def post(self):
    prefecture = self.request.get('prefecture')
    #preGql = Prefecture.gql("WHERE prefecture_number=:1 ",int(prefecture))
    preGql = Prefecture.gql("WHERE prefecture_name=:1 ",prefecture)
    prefectureid = "";
    for pg in preGql:
      prefectureid = pg.key().id()
    datas = Prefecture.get_by_id(long(prefectureid))
    staLine = datas.stationline_set
    sortList = list()
    for sortData in staLine:
      sortList.append(sortData)
    sortList.sort(key=operator.attrgetter('station_line_name'))
    lineList = list()
    for sl in sortList:
      lineList.append(sl.station_line_name)


    json = simplejson.dumps(lineList, ensure_ascii=False)
    self.response.content_type = 'application/json'
    self.response.out.write(json)

class indexSearchStation(webapp.RequestHandler):
  def post(self):
    line = self.request.get('line')
    staGql = StationLine.gql("WHERE station_line_name=:1 ",line)
    for st in staGql:
      stationlineid = st.key().id()
    datas = StationLine.get_by_id(long(stationlineid))
    station = datas.station_set
    sortList = list()
    for sortData in station:
      sortList.append(sortData)
    sortList.sort(key=operator.attrgetter('station_name'))

    lineList = list()
    for st in sortList:
      lineList.append(st.station_name)

    json = simplejson.dumps(lineList, ensure_ascii=False)
    self.response.content_type = 'application/json'
    self.response.out.write(json)

  def get(self):
      line = self.request.get('line')
      staGql = StationLine.gql("WHERE station_line_name=:1 ",line)
      for st in staGql:
        stationlineid = st.key().id()
      datas = StationLine.get_by_id(long(stationlineid))
      station = datas.station_set
      sortList = list()
      for sortData in station:
        sortList.append(sortData)
      sortList.sort(key=operator.attrgetter('station_name'))

      lineList = list()
      for st in sortList:
        lineList.append(st.station_name)

      json = simplejson.dumps(lineList, ensure_ascii=False)
      self.response.content_type = 'application/json'
      self.response.out.write(json)

class indexMakeMapHandler(webapp.RequestHandler):
  def post(self):
    prefecture = self.request.get('prefecture')
    gqlAlbumDatas = Album.gql("WHERE search_index =:1 limit 0, 100", prefecture)
    sortList = list()
    for AlbumData in gqlAlbumDatas:
      sortList.append(AlbumData)
    sortList.sort(key=operator.attrgetter('watch_counter'))

    AlbumDatas = list()
    albumCount = len(sortList)
    if albumCount > 0:
      for AlbumData in sortList:
        if AlbumData.picture_counter !=0:
          if AlbumData.latitude is not None and AlbumData.longitude is not None:
            data = list()
            data.append(AlbumData.key().id())
            data.append(AlbumData.title)
            data.append(AlbumData.latitude)
            data.append(AlbumData.longitude)
            AlbumDatas.append(data)
    else:
      AlbumDatas.append("none")

    json = simplejson.dumps(AlbumDatas, ensure_ascii=False)
    self.response.content_type = 'application/json'
    self.response.out.write(json)

class indexAboutsiteHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    loginFlg = ""
    user_top_link = ""
    if user is not None:
        loginFlg = 1
    else:
        user_top_link = users.create_login_url(PROTOCOLHTTPS+DOMAIN+"/user")

    params = {
        'user_top_link' : user_top_link,
        'loginFlg'      : loginFlg
    }
    fpath = os.path.join(os.path.dirname(__file__),'template/user','aboutsite.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

class indexPolicyHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    loginFlg = ""
    user_top_link = ""
    if user is not None:
        loginFlg = 1
    else:
        user_top_link = users.create_login_url(PROTOCOLHTTPS+DOMAIN+"/user")

    params = {
        'user_top_link' : user_top_link,
        'loginFlg'      : loginFlg
    }
    fpath = os.path.join(os.path.dirname(__file__),'template/user','policy.html')
    html = template.render(fpath,params)
    self.response.out.write(html)