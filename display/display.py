#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import os.path
import MySQLdb
import hashlib
import ConfigParser

#import tornado.auth
#import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
define("port", default=8091, help="run on the given port", type=int)

reload(sys)
sys.setdefaultencoding("utf-8")

# 读取配置文件
config = ConfigParser.ConfigParser()
config.read('../config.conf')

db_host = config.get("mysql","db_host")
db_port = config.getint("mysql","db_port")
db_user = config.get("mysql","db_user")
db_passwd = config.get("mysql","db_pass")
db_database = config.get("mysql","db_database")
db_charset = config.get("mysql","db_charset")


# MD5加密模块
def Md5(str):
    code = hashlib.md5()
    code.update(str)
    return code.hexdigest()

# 数据库模块
def Connect_Database(self,sql):
    try:
        cursor=self.application.db.cursor()
        cursor.execute(sql)
        res = cursor.fetchone()[0]
        self.application.db.commit()
        return res
    except MySQLdb.Error,e:
        self.application.db.rollback()
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        return None


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/schedule/openid=(.*)&value=(.*)", ScheduleHandler),
            (r"/exam/openid=(.*)&value=(.*)", ExamHandler),
            (r"/score/openid=(.*)&value=(.*)", ScoreHandler),
            (r".*", BaseHandler)
        ]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )

        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = MySQLdb.connect(host=db_host,user=db_user,passwd=db_passwd,db=db_database,port=db_port,charset=db_charset)

class ScheduleHandler(tornado.web.RequestHandler):

    def get(self,openid,get_value):
        #从数据库获取value值并进行加密对比
        sql="select value from user where openid = '%s'"%openid
        source_value = Md5(Connect_Database(self,sql))
        if get_value == source_value:
            sql="select schedule from schedule where openid = '%s'"%openid
            results = Connect_Database(self,sql)
            try:
                dict_results = eval(results) #完整的信息字典
            except:
                dict_results = {}
            self.render("schedule.html",dict_results = dict_results)

        else:
            self.render("illegal.html")


class ExamHandler(tornado.web.RequestHandler):

    def get(self,openid,get_value):
        #从数据库获取value值并进行加密对比
        sql="select value from user where openid = '%s'"%openid
        source_value = Md5(Connect_Database(self,sql))
        if get_value == source_value:
            sql="select exam from exam where openid = '%s'"%openid
            results = Connect_Database(self,sql)
            try:
                dict_results = eval(results) #完整的信息字典
            except:
                dict_results = {}

            dict_title = {} #为select制作的精简字典
            for key in dict_results:
                dict_title[key] = dict_results[key]['course']
            self.render("exam.html",dict_title = dict_title,dict_results = dict_results)

        else:
            self.render("illegal.html")


class ScoreHandler(tornado.web.RequestHandler):

    def get(self,openid,get_value):
        #从数据库获取value值并进行加密对比
        sql="select value from user where openid = '%s'"%openid
        source_value = Md5(Connect_Database(self,sql))
        if get_value == source_value:
            sql="select score from score where openid = '%s'"%openid
            results = Connect_Database(self,sql)
            try:
                dict_results = eval(results) #完整的信息字典
            except:
                dict_results = {}

            dict_title = {} #为select制作的精简字典
            for key in dict_results:
                dict_title[key] = dict_results[key]['course']


            self.render("score.html",dict_title = dict_title,dict_results = dict_results)

        else:
            self.render("illegal.html")


class BaseHandler(tornado.web.RequestHandler):

    def get(self):
        self.write_error(404)

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('404.html')
        elif status_code == 500:
            self.render('500.html')
        else:
            self.write('error:' + str(status_code))


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
