#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import os
import wsgiref.handlers
import md5
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.api import images
###########index#############################
from app.indexHandler import indexHandler
from app.indexHandler import indexSearchLine
from app.indexHandler import indexSearch
from app.indexHandler import indexSearchStation
from app.indexHandler import indexMakeMapHandler
from app.indexHandler import indexAboutsiteHandler
from app.indexHandler import indexPolicyHandler
###########index#############################
###########album#############################
from app.albumHandler import AlbumListHandler
from app.albumHandler import AlbumInsertHandler
from app.albumHandler import AlbumInsertEndHandler
from app.albumHandler import AlbumSlideshowHandler
from app.albumHandler import AlbumGetAddress
from app.albumHandler import AlbumDetailHandler
from app.albumHandler import AlbumDeleteEndHandler
from app.albumHandler import AlbumUpdateHandler
from app.albumHandler import AlbumUpdateEndHandler
from app.albumHandler import AlbumMakeSlideshowHandler
from app.albumHandler import AlbumAddAlbumHandler
from app.albumHandler import AlbumOrderpictureHandler
from app.albumHandler import AlbumOrderpictureEndHandler
from app.albumHandler import AlbumUpdateSlideshowHandler
from app.albumHandler import AlbumUpdateSlideshowEndHandler
from app.albumHandler import AlbumDeleteSlideshowHandler
from app.albumHandler import AlbumInsertBookMarkHandler
from app.albumHandler import AlbumBookMarkHandler
###########albumend#############################
###########user#############################
from app.userHandler import UserUpdateHandler
from app.userHandler import UserUpdateEndHandler
###########userEnd#############################
from app.pictureHandler import PictureInsertHandler
from app.pictureHandler import PictureInsertEndHandler
from app.pictureHandler import PictureUpdateEndHandler
from app.pictureHandler import PictureListHandler
from app.pictureHandler import PictureDeleteEndHandler
from app.inquiryHandler import InquiryInsertHandler
from app.inquiryHandler import InquiryFormHandler
###########adminPicture#############################
from app.adminPictureHandler import AdminPictureInsertHandler
from app.adminPictureHandler import AdminPictureInsertEndHandler
from app.adminPictureHandler import AdminPictureUpdateHandler
from app.adminPictureHandler import AdminPictureUpdateEndHandler
from app.adminPictureHandler import AdminPictureListHandler
from app.adminPictureHandler import AdminPictureDetailHandler
from app.adminPictureHandler import AdminPictureDeleteConfirmHandler
from app.adminPictureHandler import AdminPictureDeleteEndHandler
from app.imgHandler import ImgMinHandler
from app.imgHandler import ImgSmallHandler
from app.imgHandler import ImgMiddleHandler
from app.imgHandler import ImgBigHandler

###########adminUser#############################
from app.adminUserHandler import AdminUserInsertHandler
from app.adminUserHandler import AdminUserInsertEndHandler
from app.adminUserHandler import AdminUserUpdateHandler
from app.adminUserHandler import AdminUserUpdateEndHandler
from app.adminUserHandler import AdminUserListHandler
from app.adminUserHandler import AdminUserDetailHandler
from app.adminUserHandler import AdminUserDeleteConfirmHandler
from app.adminUserHandler import AdminUserDeleteEndHandler
from app.adminUserHandler import AdminUserShowPictureHandler
from app.adminUserHandler import AdminUserShowAlbumHandler
from app.adminUserHandler import AdminUserGetAddress
###########adminAlbum#############################
from app.adminAlbumHandler import AdminAlbumInsertHandler
from app.adminAlbumHandler import AdminAlbumInsertEndHandler
from app.adminAlbumHandler import AdminAlbumUpdateHandler
from app.adminAlbumHandler import AdminAlbumUpdateEndHandler
from app.adminAlbumHandler import AdminAlbumListHandler
from app.adminAlbumHandler import AdminAlbumDetailHandler
from app.adminAlbumHandler import AdminAlbumDeleteConfirmHandler
from app.adminAlbumHandler import AdminAlbumDeleteEndHandler
from app.adminAlbumHandler import AdminAlbumAddAlbumHandler
from app.adminAlbumHandler import AdminAlbumAllpictureHandler
from app.adminAlbumHandler import AdminAlbumOrderpictureHandler
from app.adminAlbumHandler import AdminAlbumDeleteAlbumHandler
from app.adminAlbumHandler import AdminAlbumSlideshowHandler
from app.adminAlbumHandler import AdminAlbumOrderpictureEndHandler
from app.adminAlbumHandler import AdminAlbumGetAddress
from app.adminAlbumHandler import AdminAlbumMakeSlideshowHandler
from app.adminAlbumHandler import AdminAlbumSlideshowAlbumListHandler
from app.adminAlbumHandler import AdminAlbumUpdateSlideshowHandler
from app.adminAlbumHandler import AdminAlbumUpdateSlideshowEndHandler
from app.adminAlbumHandler import AdminAlbumDeleteSlideshowHandler
from app.adminImportHandler import AdminPrefectureImport

def main():
    admin="admin"
    application = webapp.WSGIApplication(
                                         [
                                          #('/picture'               , MainHandler),
                                          #('/picture/index'         , MainHandler),
                                          ('/'                              , indexHandler),
                                          ('/index'                         , indexHandler),
                                          ('/indexsearch'                   , indexSearch),
                                          ('/aboutsite'                     , indexAboutsiteHandler),
                                          ('/policy'                        , indexPolicyHandler),
                                          ('/slideshow'                     , AlbumSlideshowHandler),
                                          ('/index/makemap'                 , indexMakeMapHandler),
                                          ('/user/inquiry/insert'           , InquiryInsertHandler),
                                          ('/user/inquiry'                  , InquiryFormHandler),
                                          ('/index/searchline'              , indexSearchLine),
                                          ('/index/searchstation'           , indexSearchStation),
                                          ('/user'                          , AlbumListHandler),
                                          ('/user/album/list'               , AlbumListHandler),
                                          ('/user/album/insert'             , AlbumInsertHandler),
                                          ('/user/album/insertend'          , AlbumInsertEndHandler),
                                          ('/user/album/update'             , AlbumUpdateHandler),
                                          ('/user/album/updateend'          , AlbumUpdateEndHandler),
                                          ('/user/album/getaddress'         , AlbumGetAddress),
                                          ('/user/album/detail'             , AlbumDetailHandler),
                                          ('/user/album/deleteend'          , AlbumDeleteEndHandler),
                                          ('/user/album/makeslideshow'      , AlbumMakeSlideshowHandler),
                                          ('/user/album/addalbum'           , AlbumAddAlbumHandler),
                                          ('/user/album/orderpicture'       , AlbumOrderpictureHandler),
                                          ('/user/album/orderpictureend'    , AlbumOrderpictureEndHandler),
                                          ('/user/album/updateslideshow'    , AlbumUpdateSlideshowHandler),
                                          ('/user/album/updateslideshowend' , AlbumUpdateSlideshowEndHandler),
                                          ('/user/album/deleteslideshow'    , AlbumDeleteSlideshowHandler),
                                          ('/user/album/insertbookmark'     , AlbumInsertBookMarkHandler),
                                          ('/user/album/bookmark'           , AlbumBookMarkHandler),
                                          ('/user/picture/insert'           , PictureInsertHandler),
                                          ('/user/picture/insertend'        , PictureInsertEndHandler),
                                          ('/user/picture/updateend'        , PictureUpdateEndHandler),
                                          ('/user/picture/list'             , PictureListHandler),
                                          ('/user/picture/deleteend'        , PictureDeleteEndHandler),
                                          ('/user/user/update'              , UserUpdateHandler),
                                          ('/user/user/updateend'           , UserUpdateEndHandler),
#                                          ('/'+admin                          , AdminMainHandler),
#                                          ('/'+admin+'/index'                 , AdminMainHandler),
                                          ('/'+admin+'/picture'               , AdminPictureListHandler),
                                          ('/'+admin+'/picture/insert'        , AdminPictureInsertHandler),
                                          ('/'+admin+'/picture/insertend'     , AdminPictureInsertEndHandler),
                                          ('/'+admin+'/picture/update'        , AdminPictureUpdateHandler),
                                          ('/'+admin+'/picture/updateend'     , AdminPictureUpdateEndHandler),
                                          ('/'+admin+'/picture/deleteconfirm' , AdminPictureDeleteConfirmHandler),
                                          ('/'+admin+'/picture/deleteend'     , AdminPictureDeleteEndHandler),
                                          ('/'+admin+'/picture/detail'        , AdminPictureDetailHandler),
                                          ('/'+admin+'/picture/list'          , AdminPictureListHandler),
                                          ('/picture/img/small'     , ImgSmallHandler),
                                          ('/picture/img/middle'    , ImgMiddleHandler),
                                          ('/picture/img/big'       , ImgBigHandler),
                                          ('/picture/img/min'       , ImgMinHandler),
                                          ('/'+admin+'/picture/img/small'     , ImgSmallHandler),
                                          ('/'+admin+'/picture/img/middle'    , ImgMiddleHandler),
                                          ('/'+admin+'/picture/img/big'       , ImgBigHandler),
                                          ('/'+admin+'/picture/img/min'       , ImgMinHandler),
                                          ('/'+admin+'/user/insert'        , AdminUserInsertHandler),
                                          ('/'+admin+'/user/insertend'     , AdminUserInsertEndHandler),
                                          ('/'+admin+'/user/update'        , AdminUserUpdateHandler),
                                          ('/'+admin+'/user/updateend'     , AdminUserUpdateEndHandler),
                                          ('/'+admin+'/user/deleteconfirm' , AdminUserDeleteConfirmHandler),
                                          ('/'+admin+'/user/deleteend'     , AdminUserDeleteEndHandler),
                                          ('/'+admin+'/user/detail'        , AdminUserDetailHandler),
                                          ('/'+admin+'/user/list'          , AdminUserListHandler),
                                          ('/'+admin+'/user/showpicture'   , AdminUserShowPictureHandler),
                                          ('/'+admin+'/user/showalbum'     , AdminUserShowAlbumHandler),
                                          ('/'+admin+'/user/getaddress'    , AdminUserGetAddress),
                                          ('/'+admin+'/album/addalbum'                 , AdminAlbumAddAlbumHandler),
                                          ('/'+admin+'/album'                          , AdminAlbumListHandler),
                                          ('/'+admin+'/album/insert'                   , AdminAlbumInsertHandler),
                                          ('/'+admin+'/album/insertend'                , AdminAlbumInsertEndHandler),
                                          ('/'+admin+'/album/update'                   , AdminAlbumUpdateHandler),
                                          ('/'+admin+'/album/updateend'                , AdminAlbumUpdateEndHandler),
                                          ('/'+admin+'/album/deleteconfirm'            , AdminAlbumDeleteConfirmHandler),
                                          ('/'+admin+'/album/deleteend'                , AdminAlbumDeleteEndHandler),
                                          ('/'+admin+'/album/detail'                   , AdminAlbumDetailHandler),
                                          ('/'+admin+'/album/list'                     , AdminAlbumListHandler),
                                          ('/'+admin+'/album/allpicture'               , AdminAlbumAllpictureHandler),
                                          ('/'+admin+'/album/orderpicture'             , AdminAlbumOrderpictureHandler),
                                          ('/'+admin+'/album/orderpictureend'          , AdminAlbumOrderpictureEndHandler),
                                          ('/'+admin+'/album/slideshow'                , AdminAlbumSlideshowHandler),
                                          ('/'+admin+'/album/makeslideshow'            , AdminAlbumMakeSlideshowHandler),
                                          ('/'+admin+'/album/slideshowalbumlist'       , AdminAlbumSlideshowAlbumListHandler),
                                          ('/'+admin+'/album/updateslideshow'          , AdminAlbumUpdateSlideshowHandler),
                                          ('/'+admin+'/album/updateslideshowend'       , AdminAlbumUpdateSlideshowEndHandler),
                                          ('/'+admin+'/album/deleteslideshow'          , AdminAlbumDeleteSlideshowHandler),
                                          ('/'+admin+'/album/getaddress'               , AdminAlbumGetAddress),
                                          ('/'+admin+'/album/deletealbum'              , AdminAlbumDeleteAlbumHandler)
                                          #('/'+admin+'/import/prefecture' , AdminPrefectureImport)
                                          ],
                                         debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
