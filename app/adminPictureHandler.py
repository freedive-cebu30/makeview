import cgi
import os
import wsgiref.handlers
from django.core.paginator import ObjectPaginator, InvalidPage
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from model.Picture import Picture
from model.User import User

FILE_MAX = 100
PAGE     = 15

class AdminPictureInsertHandler(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/picture','insert.html')
    html = template.render(fpath,'')
    self.response.out.write(html)
  def get(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/picture','insert.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

    return

class AdminPictureInsertEndHandler(webapp.RequestHandler):
  def post(self):
    try:
      user = users.get_current_user()
      if not user:
          return self.redirect('/admin/index')
      i=0
      while(i < 19):
        binary = self.request.get('binary_'+str(i))
        if not binary:
          break
        name = self.request.body_file.vars['binary_'+str(i)].filename
        mime = self.request.body_file.vars['binary_'+str(i)].headers['content-type']
        self.registerPicture(binary,name,mime,user)
        i += 1

      fpath = os.path.join(os.path.dirname(__file__),'template/admin/picture','insertend.html')
      html = template.render(fpath,'')
      self.response.out.write(html)
    except:self.errorFunc()

  def errorFunc(self):
    fpath = os.path.join(os.path.dirname(__file__),'template/admin','error.html')
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
    data.put()

class AdminPictureUpdateHandler(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    pictureid = self.request.get('pictureid')
    datas = Picture.get_by_id(long(pictureid))
    params = {'datas':datas}
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/picture','update.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

class AdminPictureUpdateEndHandler(webapp.RequestHandler):

    def post(self):
      try:
        user = users.get_current_user()
        if not user:
            return self.redirect('/admin/index')

        pictureIdList =  self.request.POST.getall("pictureid")

        for pil in pictureIdList:
          label      = self.request.get("label"+pil)
          if len(label) > 10:
            raise RuntimeError("labelMax error")
          data       = Picture.get_by_id(long(pil))
          data.label = label
          data.put()
      except:
        self.errorFunc()

    def errorFunc(self):
      fpath = os.path.join(os.path.dirname(__file__),'template/admin','error.html')
      html = template.render(fpath,'')
      self.response.out.write(html)

      return self.redirect('/admin/picture/list')

class AdminPictureListHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    page        = self.request.get('page')
    zoomFlg     = self.request.get('zoomFlg')
    searchLabel = self.request.get('searchLabel')

    try:
        page = int(page) - 1
    except:
        page = 0
    if searchLabel !="":
      datas = Picture.gql("WHERE label =:1", searchLabel)
    else:
      datas = Picture.all()

    paginator = ObjectPaginator(datas,PAGE)
    if page>=paginator.pages:
            page = paginator.pages - 1
    params = {
        "datas"       : paginator.get_page(page),
        "pages"       : range(1,paginator.pages+1),
        "page"        : page+1,
        'zoomFlg'     : zoomFlg,
        'searchLabel' : searchLabel
    }
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/picture','list.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminPictureDetailHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    pictureid = self.request.get('pictureid')
    datas = Picture.get_by_id(long(pictureid))
    params = {'datas':datas}
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/picture','detail.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminPictureDeleteConfirmHandler(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    pictureid = self.request.get('pictureid')
    datas = Picture.get_by_id(long(pictureid))
    params = {'datas':datas}
    fpath = os.path.join(os.path.dirname(__file__),'template/admin/picture','deleteconfirm.html')
    html = template.render(fpath,params)
    self.response.out.write(html)

    return

class AdminPictureDeleteEndHandler(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if not user:
        return self.redirect('/admin/index')
    pictureIdList =  self.request.POST.getall("pictureid")
    for pil in pictureIdList:
      data       = Picture.get_by_id(long(pil))
      data.delete()

    fpath = os.path.join(os.path.dirname(__file__),'template/admin/picture','deleteend.html')
    html = template.render(fpath,'')
    self.response.out.write(html)

    return


