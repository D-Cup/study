# -*- coding:utf-8 -*-
import os
from uuid import uuid4

from flask import request, session
from flask_restful import Api, Resource, marshal_with, fields, marshal, reqparse
from werkzeug.datastructures import FileStorage

import settings
from dao import query, queryAll, add, queryById, delete, deleteById, search, searchMusic
from models import User, Image, Music

api = Api()


def init_api(app):
    api.init_app(app)


class UserApi(Resource):  # 声明User资源
    def get(self):
        key = request.args.get('key')
        if key:
            result = {'state': 'fail',
                      'msg': '查无数据'}
            user = search(User, key)
            if user.count():
                result['state'] = 'ok'
                result['msg'] = 'ok'
                result['data'] = user.first().json
            return result
        users = queryAll(User)
        return {'state': 'ok', 'data': [user.json for user in users]}

    def post(self):
        name = request.form['name']
        phone = request.form['phone']
        print(name, phone)

        user = User()
        user.name = name
        user.phone = phone
        add(user)
        return {'state': 'ok', 'msg': '{}添加成功'.format(user.name)}

    def delete(self):
        id = request.args['id']
        flag = deleteById(User, id)
        return {'state': 'ok', 'flag': flag, 'msg': '{}删除成功'.format(id)}

    def patch(self):

        id = request.form['id']
        name = request.form['name']
        phone = request.form['phone']
        # print(id,name,phone)
        qs = queryById(User, id)
        if qs:
            qs.name = name
            qs.phone = phone
            add(qs)
            return {'state': 'ok', 'msg': '{}修改成功'.format(qs.name)}
        return {'state': 'fail', 'msg': '{}修改失败'}


class ImageApi(Resource):
    img_fields = {'id': fields.Integer,
                  'name': fields.String,
                  'img_url': fields.String(attribute='url'),
                  'size': fields.Integer(default=0)}
    get_out_fields = {
        'state': fields.String(default='ok'),
        'data': fields.Nested(img_fields),
        'size': fields.Integer(default=1)
    }

    #  输入的定制
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=True, help='请提供id参数')

    # @marshal_with(get_out_fields)
    def get(self):

        id = request.args.get('id')
        if id:
            img = query(Image).filter(Image.id == id).first()
            #  将对象转成输出的字段格式（Json格式）
            return marshal(img, self.img_fields)
        else:
            # 查询所有Image
            images = queryAll(Image)
            data = {'data': images, 'size': len(images)}

            #  向session中存放用户名
            session['login_name']='moliy'
            return marshal(data, self.get_out_fields)


    parser = reqparse.RequestParser()
    parser.add_argument('name',required=True,help='必须提供图片名称')
    parser.add_argument('url',required=True,help='必须提供图片路径')
    def post(self):
            args = self.parser.parse_args()
            img = Image()
            img.name =args['name']
            img.url = args['url']
            add(img)
            return {'msg':'添加图片成功'}

class MusicApi(Resource):
    music_fields = {'id': fields.Integer,
                    'name': fields.String,
                    'singer': fields.String,
                    'brand': fields.String,
                    'url': fields.String(attribute='mp3_url')}
    get_out_fields = {'state': fields.String(default='ok'),
                      'data': fields.Nested(music_fields)}
    out_fields = {'state':fields.String(default='ok'),
                  'msg':fields.String(default='查询成功'),
                  'data': fields.Nested(music_fields),
                  'tag':fields.String
                  }

    paser = reqparse.RequestParser() # 创建请求参数的解析器

    # 向参数解析器中添加请求参数说明
    paser.add_argument('key',dest='name',type=str,required=True,help='必须提供name搜索的关键字')
    paser.add_argument('id' ,type=int,help='请确定ID的参数是否为数值型')
    paser.add_argument('tag',action='append',required=True,help='至少提供一个标签')
    paser.add_argument('session',location='cookies',required=True,help='cookie中不存在session')
    @marshal_with(out_fields)
    def get(self):
        # key = request.args.get('key')
        # if key:
        #     music = searchMusic(Music, key).first()
        #     data = {'data':music}
        #     return marshal(data,self.get_out_fields)
        # musics = queryAll(Music)
        # return marshal({'data': musics}, self.get_out_fields)

        #  通过request参数解析器，开始解析请求参数
        #  如果请求参数不能阀组调教，则直接返回参数相关的help说明

        args = self.paser.parse_args()
        name = args['name']
        tag = args['tag']
        session=args.get('session')
        print('session---------------------------',session)
        musics = query(Music).filter(Music.name.like('%{}%'.format(name)))
        if musics.count():
            return {'data':musics.all(),'tag':tag}
        return {'msg':'查无此歌{}'.format(name)}



    def post(self):
        name = request.form['name']
        singer = request.form['singer']
        brand = request.form['brand']
        mp3_url=request.form['mp3_url']
        music = Music()
        music.name=name
        music.singer=singer
        music.brand=brand
        music.mp3_url=mp3_url
        add(music)
        return {'state': 'ok', 'msg': '{}添加成功'.format(name)}

    def delete(self):
        id = request.args['id']
        flag = deleteById(Music,id)
        return {'state': 'ok', 'flag': flag, 'msg': '{}删除成功'.format(id)}



class UploadApi(Resource):
    paser = reqparse.RequestParser()
    paser.add_argument('img',type=FileStorage,location='files',required=True,help='必须要提供一个名为img的File表单')

    def post(self):
        args = self.paser.parse_args()
        #  保存上传的文件
        uFile:FileStorage = args['img']
        ext = uFile.filename.split('.')[-1]
        newFileNname = str(uuid4()).replace('-','')
        newFileNname += '.'+ext
        uFile.save(os.path.join(settings.MEDIA_DIR,newFileNname))
        return {'msg':'上传成功','path':'/static/uploads/{}'.format(newFileNname)}


# 将字段添加到api对象中，并声明uri
api.add_resource(UserApi, '/user')
api.add_resource(ImageApi, '/images')
api.add_resource(MusicApi, '/musics')
api.add_resource(UploadApi,'/upload')
