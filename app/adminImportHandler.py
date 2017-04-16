import cgi
import os
import wsgiref.handlers
import csv
from StringIO import StringIO

from django.core.paginator import ObjectPaginator, InvalidPage
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from model.Picture import Picture
from model.User import User
from model.Album import Album
from model.PictureConnectAlbum import PictureConnectAlbum
from model.Prefecture import Prefecture
from model.StationLine import StationLine
from model.Station import Station

class AdminPrefectureImport(webapp.RequestHandler):
  def post(self):
    case = self.request.get('case')
    if case=="1":
      rawfile = self.request.get('file')
      csvfile = csv.reader(StringIO(rawfile))
      for row in csvfile:
        m = Prefecture(
            prefecture_number = int(row[0]),
            prefecture_name = unicode(row[1], 'cp932')
          )
        m.put()
    elif case=="2":
      rawfile = self.request.get('line')
      csvfile = csv.reader(StringIO(rawfile))
      for row in csvfile:
        PreDatas = Prefecture.gql("WHERE prefecture_number = :1 ", int(row[0]))
        for preData in PreDatas:
          id = preData.key().id()
        prefecture = Prefecture.get_by_id(long(id))
        m = StationLine(
            prefecture          = prefecture,
            station_line_number = int(row[2]),
            station_line_name   = unicode(row[1], 'cp932')
          )
        m.put()
    elif case=="3":
      rawfile = self.request.get('station')
      csvfile = csv.reader(StringIO(rawfile))
      for row in csvfile:
        StaDatas = StationLine.gql("WHERE station_line_number = :1 ", int(row[0]))
        for StaData in StaDatas:
          id = StaData.key().id()
        stationline = StationLine.get_by_id(long(id))
        m = Station(
            station_line    = stationline,
            station_name    = unicode(row[1], 'cp932'),
            station_number  = int(row[2])
          )
        m.put()
    self.redirect(self.request.uri)
  def get(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/import','prefecture.html')
    html = template.render(fpath,'')
    self.response.out.write(html)
