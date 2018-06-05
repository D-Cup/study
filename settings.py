# -*- coding:utf-8 -*-
import os

# 上传文件存放的位置
BASE_DIR = os.path.dirname(os.path.abspath(__name__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
MEDIA_DIR = os.path.join(STATIC_DIR, 'uploads')

class Config():
    ENV = 'development'
    DEBUG = 'True'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:8227099@120.79.223.66/flaskUsers'
    SQLALCHEMY_TRACK_MODIFICATIONS='False'
    SECRET_KEY = '123'

