from google.appengine.ext import webapp
from google.appengine.api import images
from google.appengine.api import users
from model.Picture import Picture
from google.appengine.api import memcache

class ImgMinHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user is None:
        return self.redirect('/admin/index')
    if self.request.get('pictureid'):
      pictureid = self.request.get('pictureid')
      img = memcache.get(pictureid)
      if img is None:
        img = Picture.get_by_id(long(pictureid))
        memcache.add(pictureid, img, 20)

      #if img.user.email != user.email():
      #  img=''
      if img:
        newimg = images.Image(img.binary)
        newimg.resize(width=80, height=80)
        newimg.im_feeling_lucky()
        if img.mime=='image/png':
          smallimg = newimg.execute_transforms(output_encoding=images.PNG)
        else:
          img.mime=='image/jpeg'
          smallimg = newimg.execute_transforms(output_encoding=images.JPEG)
        self.response.headers['Content-Type'] = img.mime
        self.response.out.write(smallimg)
      else:
          self.error(404)
    else:
      self.error(404)

class ImgSmallHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
#    if user is None:
#        return self.redirect('/admin/index')
    if self.request.get('pictureid'):
      pictureid = self.request.get('pictureid')
      img = memcache.get(pictureid)
      if img is None:
        img = Picture.get_by_id(long(pictureid))
        memcache.add(pictureid, img, 20)
      if img:
        newimg = images.Image(img.binary)
        newimg.resize(width=120, height=120)
        newimg.im_feeling_lucky()
        if img.mime=='image/png':
          smallimg = newimg.execute_transforms(output_encoding=images.PNG)
          self.response.headers['Content-Type']='image/png'
          self.response.out.write(smallimg)
        else:
          img.mime=='image/jpeg'
          smallimg = newimg.execute_transforms(output_encoding=images.JPEG)
          self.response.headers['Content-Type']='image/jpeg'
          self.response.out.write(smallimg)
      else:
          self.error(404)
    else:
      self.error(404)

class ImgMiddleHandler(webapp.RequestHandler):
  def get(self):
#    user = users.get_current_user()
#    if user is None:
#        return self.redirect('/admin/index')
    if self.request.get('pictureid'):
      pictureid = self.request.get('pictureid')
      img = memcache.get(pictureid)
      if img is None:
        img = Picture.get_by_id(long(pictureid))
        memcache.add(pictureid, img, 20)
      if img:
        newimg = images.Image(img.binary)
        newimg.resize(width=500, height=400)
        newimg.im_feeling_lucky()
        if img.mime=='image/png':
          smallimg = newimg.execute_transforms(output_encoding=images.PNG)
          self.response.headers['Content-Type'] = 'image/png'
          self.response.out.write(smallimg)
        else:
          img.mime=='image/jpeg'
          smallimg = newimg.execute_transforms(output_encoding=images.PNG)
          self.response.headers['Content-Type'] = 'image/jpeg'
          self.response.out.write(smallimg)
      else:
          self.error(404)
    else:
      self.error(404)

class ImgBigHandler(webapp.RequestHandler):
  def get(self):
#    user = users.get_current_user()
#    if user is None:
#        return self.redirect('/admin/index')
    if self.request.get('pictureid'):
      pictureid = self.request.get('pictureid')
      img = memcache.get(pictureid)
      if img is None:
        img = Picture.get_by_id(long(pictureid))
        memcache.add(pictureid, img, 20)
      if img:
        newimg = images.Image(img.binary)
        newimg.resize(width=600, height=500)
        newimg.im_feeling_lucky()
        if img.mime=='image/png':
          smallimg = newimg.execute_transforms(output_encoding=images.PNG)
          self.response.headers['Content-Type'] = 'image/png'
          self.response.out.write(smallimg)
        else:
          img.mime=='image/jpeg'
          smallimg = newimg.execute_transforms(output_encoding=images.PNG)
          self.response.headers['Content-Type'] = 'image/jpeg'
          self.response.out.write(smallimg)
      else:
          self.error(404)
    else:
      self.error(404)

