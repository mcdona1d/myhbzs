#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import ConfigParser

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from click import *

from wechat_sdk import WechatBasic
from wechat_sdk.messages import (
    TextMessage, VoiceMessage, ImageMessage, VideoMessage, LinkMessage, LocationMessage, EventMessage
)

from tornado.options import define, options
define("port", default=8090, help="run on the given port", type=int)

reload(sys)
sys.setdefaultencoding("utf-8")

# 读取配置文件
config = ConfigParser.ConfigParser()
config.read('config.conf')

token = config.get("wechat","token")
appid = config.get("wechat","appid")
appsecret = config.get("wechat","secret")


# 关注事件
def Event_subscribe():
    return {'types':'news','articles':Subscribe_help()}

# 取消关注事件
def Event_unsubscribe(openid):
    return Unbind_user(openid)

# 文字信息处理模块
def Match_message(openid,content):
    bind_re = ur'\u7ed1\u5b9a' #'绑定'转unicode
    unbind_re = ur'\u89e3\u7ed1' #'解绑'转unicode
    title_re = ur'\u4e66\u540d' #'书名'转unicode
    author_re = ur'\u4f5c\u8005' #'作者'转unicode
    detail_re = ur'\u8be6\u60c5' #'详情'转unicode
    evaluate_re = ur'\u4e66\u8bc4' #'书评'转unicode
    favorites_re = ur'\u6536\u85cf' #'收藏'转unicode
    unfavorites_re = ur'\u53d6\u6d88\u6536\u85cf' #'取消收藏'转unicode

    if re.match(bind_re,content.decode('utf8')):
        return {'types':'news','articles':Bind_user(openid,content)}
    elif re.match(unbind_re,content.decode('utf8')):
        return {'types':'news','articles':Unbind_user(openid)}
    elif re.match(title_re,content.decode('utf8')):
        return {'types':'news','articles':Retrieve_books(openid,content,"title")}
    elif re.match(author_re,content.decode('utf8')):
        return {'types':'news','articles':Retrieve_books(openid,content,"author")}
    elif re.match(detail_re,content.decode('utf8')):
        return {'types':'news','articles':Detail_books(openid,content)}
    elif re.match(evaluate_re,content.decode('utf8')):
        return {'types':'news','articles':Evaluate_books(openid,content)}
    elif re.match(favorites_re,content.decode('utf8')):
        return {'types':'news','articles':Favorite_books(openid,content)}
    elif re.match(unfavorites_re,content.decode('utf8')):
        return {'types':'news','articles':Unfavorite_books(openid,content)}
    else:
        return {'types':'text','content':TuringRobot(openid,content)} #调用聊天机器人接口

# 按键信息处理模块
def Match_click(click,openid):
    if click == 'btn_calender':
        return {'types':'news','articles':Click_calender()}
    elif click == 'btn_party':
        return {'types':'news','articles':Click_party()}
    elif click == 'btn_warn':
        return {'types':'news','articles':Click_warn()}
    elif click == 'btn_schedule':
        return {'types':'news','articles':Click_zf_schedule(openid)}
    elif click == 'btn_score':
        return {'types':'news','articles':Click_zf_score(openid)}
    elif click == 'btn_exam':
        return {'types':'news','articles':Click_zf_exam(openid)}
    elif click == 'btn_user':
        return {'types':'news','articles':Click_zf_userinfo(openid)}
    elif click == 'btn_weather':
        return {'types':'news','articles':Click_weather()}
    elif click == 'btn_collect':
        return {'types':'news','articles':Click_collect(openid)}
    elif click == 'btn_network_status':
        return {'types':'text','content':Click_network_status()}
    elif click == 'btn_network_offline':
        return {'types':'text','content':Click_network_offline()}
    elif click == 'btn_help':
        return {'types':'news','articles':Click_help()}
    else:
        return {'types':'text','content':"未知的按钮"}

# 实例化对象
wechat = WechatBasic(token=token, appid=appid, appsecret=appsecret)

class WeChatHandler(tornado.web.RequestHandler):

    def prepare(self):
        timestamp = self.get_argument('timestamp', '')
        nonce = self.get_argument('nonce', '')
        signature = self.get_argument('signature', '')
        if not wechat.check_signature(
            timestamp=timestamp,
            nonce=nonce,
            signature=signature
        ):
            self.finish('Unvailed request.')

    def get(self):
        echostr = self.get_argument('echostr', '')
        self.write(echostr)

    def post(self):
        body = self.request.body
        wechat.parse_data(body)
        self.set_header("Content-Type",
                        "application/xml;charset=utf-8")
        reply = wechat.get_message()

        response = None
        if isinstance(reply, TextMessage): #文字信息处理
            result = Match_message(reply.source,reply.content)
            if result['types'] == 'text' :
                response = wechat.response_text(content=result['content'])
            elif result['types'] == 'image' :
                response = wechat.response_image(media_id=result['media_id'])
            elif result['types'] == 'news' :
                response = wechat.response_news(articles=result['articles'])
            else :
                pass
        elif isinstance(reply, VoiceMessage): #语音信息处理
            response = wechat.response_text(content=u'我还不能处理语音信息')
        elif isinstance(reply, ImageMessage): #图片信息处理
            response = wechat.response_text(content=u'我还不能处理图片信息')
        elif isinstance(reply, VideoMessage): #视频信息处理
            response = wechat.response_text(content=u'我还不能处理视频信息')
        elif isinstance(reply, LinkMessage): #链接信息处理
            response = wechat.response_text(content=u'我还不能处理链接信息')
        elif isinstance(reply, LocationMessage): #地理位置信息处理
            response = wechat.response_text(content=u'我还不能处理地理位置信息')
        elif isinstance(reply, EventMessage):  # 事件信息处理
            if reply.type == 'subscribe':  # 关注事件(包括普通关注事件和扫描二维码造成的关注事件)
                if reply.key and reply.ticket:  # 如果 key 和 ticket 均不为空，则是扫描二维码造成的关注事件
                    response = wechat.response_text(content=u'用户尚未关注时的二维码扫描关注事件')
                else:
                    result =  Event_subscribe()
                    response = wechat.response_news(articles=result['articles'])
            elif reply.type == 'unsubscribe': #取消关注处理
                response = Event_unsubscribe(reply.source)
            elif reply.type == 'scan': #已关注时的二维码扫描事件
                response = wechat.response_text(content=u'用户已关注时的二维码扫描事件')
            elif reply.type == 'location': #上报地理位置事件
                response = wechat.response_text(content=u'上报地理位置事件')
            elif reply.type == 'click': #自定义菜单点击事件
                result = Match_click(reply.key,reply.source)
                if result['types'] == 'text' :
                    response = wechat.response_text(content=result['content'])
                elif result['types'] == 'image' :
                    response = wechat.response_image(media_id=result['media_id'])
                elif result['types'] == 'news' :
                    response = wechat.response_news(articles=result['articles'])
                else :
                    pass
            elif reply.type == 'view': #自定义菜单跳转链接事件
                response = wechat.response_text(content=u'自定义菜单跳转链接事件')
            elif reply.type == 'templatesendjobfinish': #模板消息事件
                response = wechat.response_text(content=u'模板消息事件')
        self.write(str(response))

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", WeChatHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
