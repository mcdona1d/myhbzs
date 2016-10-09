# -*- coding: utf-8 -*-
import re
import time
import json
import zlib
import urllib
import urllib2
import MySQLdb
import hashlib
import socket
import traceback
import cookielib
#import codecs
import ConfigParser
from bs4 import BeautifulSoup
from random import Random

# 读取配置文件
config = ConfigParser.ConfigParser()
config.read('config.conf')

db_host = config.get("mysql","db_host")
db_port = config.getint("mysql","db_port")
db_user = config.get("mysql","db_user")
db_passwd = config.get("mysql","db_pass")
db_database = config.get("mysql","db_database")

jw_url = config.get("website","jw_url")
library_url = config.get("website","library_url")
douban_url = config.get("website","douban_url")

socket_ip = config.get("socket","ip")
socket_port = config.getint("socket","port")

now_year = config.get("date","now_year")
now_semester = config.getint("date","now_semester")


# 随机数生成模块
def Random_value(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str+=chars[random.randint(0, length)]
    return str


# MD5加密模块
def Md5(str):
    code = hashlib.md5()
    code.update(str)
    return code.hexdigest()


# 解压缩模块
def decompress(compress_content):
    decompressor = zlib.decompressobj()
    content = decompressor.decompress(compress_content)
    return content


# Log输出模块
def log(type,log):
    get_time =  time.strftime('%Y-%m-%d %A %X %Z', time.localtime( time.time() ) )
    if type == "Info":
        print "Info : " + get_time + log
    elif type == "Error":
        print "Error : " + get_time + log


# 数据库模块
def Connect_Database(sql,param,operation):
    #try:
        conn=MySQLdb.connect(host=db_host,user=db_user,passwd=db_passwd,db=db_database,port=db_port)
        cursor=conn.cursor()
        cursor.execute(sql,param)
        if operation == 'commit':
            conn.commit()
            conn.close()
            return "Success"
        elif operation == 'select':
            results = cursor.fetchone()
            conn.commit()
            conn.close()
            return results
        elif operation == 'selectall':
            results = cursor.fetchall()
            conn.commit()
            conn.close()
            return results
        else :
            return "Wrong Operation"
    #except MySQLdb.Error,e:
    #    conn.rollback()
    #    print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    #    return None


def Redis_chche(key,value,expire,operation):
    r = redis.Redis(host='localhost', port=6379, db=0)
    if operation == 'save':
        r.set(key, value)
        r.expire(key, expire)
        return "Save Success"

    elif operation == 'load':
        return r.get(key)
    else :
        return "Wrong Operation"


# 连接抓取服务器
def Get_socket_server(command_dict):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4.5)
    try:
        s.connect((socket_ip, socket_port))
    except socket.timeout:
        print 'Connection Timeout'
        s.close()
        return None

    except Exception, e:
        msg = traceback.format_exc()
        print 'Connection Error:', msg
        return None


    s.send(command_dict)

    # 利用shutdown()函数使socket双向数据传输变为单向数据传输
    # 该参数表示了如何关闭socket。具体为：0表示禁止将来读；1表示禁止将来写；2表示禁止将来读和写
    s.shutdown(1)
    print 'Send Request Complete.'


    receive = []
    while 1:
        buff = s.recv(4096)
        if not len(buff):
            break
        else:
            receive.append(buff)

    s.close()
    data = ''.join(receive)
    print 'Receive information length:',len(data)
    return data


# 数据库查询用户信息
def Get_userinfo(openid):
    sql = "select * from user where openid = %s"
    user = Connect_Database(sql,openid,'select')
    if user == None:
        return None
    else:
        user_dict = { 'username' : user[2], 'password' : user[3], 'value' : user[1] }
        return user_dict


# 用户绑定
def Bind_user(openid,content):

    '''
    1.检查绑定情况
    2.检查输入格式
    3.模拟登录验证帐号信息
    4.生成随机字符串
    5.写入数据库绑定成功
    '''
    
    #1.检查绑定情况
    user = Get_userinfo(openid)

    if (user == None):
        #2.检查输入格式
        try:
            bind_re= r"#([0-9]*)#(\w*)"
            bd_result = re.search(bind_re,content)
            std_id = bd_result.group(1)
            std_pass = bd_result.group(2)
        except:
            reply_msg = ("您未按照约定格式输入学号密码，请检查后重试\n"
                         "正确格式为 发送 “绑定#学号#密码”，例如 “绑定#12111000#password”")
        else:
            #3.模拟登录验证帐号信息
            command_dict = {
                'type': 'jw',
                'username': std_id,
                'password': std_pass,
                'module': 'login',
                'jw_url': jw_url,
                'now_year': now_year,
                'now_semester': now_semester
            }
            print str(command_dict)
            try:
                Sname = Get_socket_server(str(command_dict))
                #print result
            except:
                reply_msg = "暂时无法连接绑定服务器，请稍候再试"
            else:
                if len(Sname) != 0:
                    #4.生成随机字符串
                    value = Random_value(randomlength=8)
                    #5.写入数据库绑定成功
                    sql = "insert into user (openid,value,jw_id,jw_pass) values (%s,%s,%s,%s)"
                    param = (openid,value,std_id,std_pass)
                    result = Connect_Database(sql,param,'commit')
                    if result == 'Success':
                        reply_msg = ("恭喜您！\n"
                                     "%s同学，账号绑定成功！\n"
                                     "您现在可以使用本助手的全部功能！\n"
                                     "如需解绑请回复 “解绑”")%Sname
                    else :
                        reply_msg = "代码Bug，麻烦请将出现错误的操作截图发给我，谢谢"
                else:
                    reply_msg = "账号密码错误！绑定失败，请检查账号密码后重试。"

    else:
        reply_msg = "此微信账号已经绑定学号，不能重复绑定！请先解绑后操作"

    Bind_user_message = [
    {
        'title': u'账户绑定结果',
        'description': reply_msg,
        'picurl': u'',
        'url': u'',
    }]
    return Bind_user_message


# 用户解绑
def Unbind_user(openid):

    user = Get_userinfo(openid)
    if (user == None):
        reply_msg = "账号未绑定,无法执行解绑操作"
    else:
        try:
            sql = "delete from user where openid = %s"
            result = Connect_Database(sql,openid,'commit')
            if result == "Success":
                reply_msg = "账号解绑成功"
            else:
                reply_msg = "未知错误"
        except MySQLdb.Error,e:
            reply_msg = "数据库异常，解绑失败，请稍候重试"

    Unbind_user_message = [
    {
        'title': u'账户解绑结果',
        'description': reply_msg,
        'picurl': u'',
        'url': u'',
    }]
    return Unbind_user_message


# 图灵机器人接口
def TuringRobot(openid,content):

    api_key = '497d37e77128e2a511e1133dc18338b9'
    location = '河北省沧州市黄骅市'
    #tulingurl = 'http://www.tuling123.com/openapi/api?key=%s&info=%s&userid=%s&loc=%s'%(codecs.encode(api_key,'utf-8'),codecs.encode(content,'utf-8'),codecs.encode(openid,'utf-8'),codecs.encode(location,'utf-8'))
    tulingurl = 'http://www.tuling123.com/openapi/api?key=%s&info=%s&userid=%s&loc=%s'%(api_key,content,openid,location)
    getreply = urllib2.urlopen(tulingurl).read()
    loadreply = str(json.loads(getreply)['code'])
    if loadreply == '100000':
        reply_msg = json.loads(getreply)['text']
    elif loadreply == '200000':
        reply_msg = json.loads(getreply)['text'] + "\n<a href='%s'>点此查看详情</a>"%json.loads(getreply)['url']
    elif loadreply == '302000':
        # 新闻类型接口 待开发
        reply_msg = json.loads(getreply)['text']
    elif loadreply == '308000':
        # 菜谱类型接口 待开发
        reply_msg = json.loads(getreply)['text']
    else:
        print json.loads(getreply)['text']
        reply_msg = "我被你们玩死啦 (@~@)? "

    #return "小助：" + reply_msg
    return reply_msg


# 检索图书（抓取端处理数据版本，因抓取端性能弱，暂不使用）
def Retrieve_books2(content):
    #try:
        retrieve_re= r"#(.*)"
        retrieve_result = re.search(retrieve_re,content)
        title = retrieve_result.group(1)

        command_dict = {
            'type': 'library',
            'title': title,
            'library_url': library_url
        }
        print str(command_dict)
        try:
            msg = Get_socket_server(str(command_dict))
        except:
            msg = "暂时无法连接抓取服务器，请稍候再试"
            book = [
            {
                'title': u'图书查询结果',
                'description': msg,
                'picurl': u'',
                'url': u'',
            }]


        return book

    #except:
        #return "图书查询格式有误，请重新输入"


# 检索图书（云端处理数据版本）
def Retrieve_books(openid,content,types):
    try:
        retrieve_re= r"#(.*)"
        retrieve_result = re.search(retrieve_re,content)
        content = retrieve_result.group(1)

    except:
        msg = '图书查询输入格式有误，请重新输入'

    else:
        redis_key = types + ':' + content.encode("utf-8")
        print redis_key
        data = Redis_chche(redis_key,None,None,"load")
        if data:
            data = eval(data)
            msg = '以下是查询到的图书信息：'
            for i in data:
                finaldata = data[i]

                msg = msg + ( '\n\n'
                              '序号： %s \n'
                              '书名： %s \n'
                              '作者： %s \n'
                              '出版社： %s \n'
                              '索书号： %s \n'
                              '文献类型： %s ')%( i,finaldata['title'],finaldata['author'],finaldata['publisher'],\
                              finaldata['loc'],finaldata['types'] )

        else:
            command_dict = {
                'type': types,
                'content': content,
                'library_url': library_url
            }
            #print str(command_dict)
            try:
                compress_retrieve_page = Get_socket_server(str(command_dict))
                retrieve_page = str(decompress(compress_retrieve_page))
                soup = BeautifulSoup(retrieve_page, "html.parser")
            except:
                msg = "暂时无法连接抓取服务器，请稍候再试"
            else:
                try:
                    table = soup.find("table", {"id": "result_content"})
                    rows = (len(table.findAll('tr')))

                    dict_list = {}
                    i = 0
                    msg = '以下是查询到的图书信息：'
                    # set to run through rows
                    for row in table.findAll('tr')[1:min(rows,8)]:
                        col = row.findAll('td')
                        num = col[0].getText() #序号
                        title = col[1].getText() #书名
                        bookid = col[1].a['href'][17:]
                        author = col[2].getText() #作者
                        publisher = col[3].getText() #出版信息
                        loc = col[4].getText() #索书号
                        types = col[5].getText() #文献类型

                        i = i + 1

                        dict_list[i] = { 'bookid':bookid,
                                         'title':title,
                                         'author':author,
                                         'publisher':publisher,
                                         'loc':loc,
                                         'types':types }

                        msg = msg + ( '\n\n'
                                      '序号： %s \n'
                                      '书名： %s \n'
                                      '作者： %s \n'
                                      '出版社： %s \n'
                                      '索书号： %s \n'
                                      '文献类型： %s ')%( i,title,author,publisher,loc,types )

                except:
                    msg = '很抱歉，没有找到您需要的图书信息。'
                else:
                    if len(msg.encode("utf-8")) > 2048 :
                        msg = '获取到的数据过长，无法显示。\n此情况属于微信接口限制，正在努力优化，请谅解。'
                    print "Personal data:" + Redis_chche(openid,dict_list,3600,"save")
                    print "Global data:" + Redis_chche(redis_key,dict_list,604800,"save")

    book = [
    {
        'title': u'图书查询结果',
        'description': msg,
        'picurl': u'',
        'url': u'',
    }]

    return book


def Favorite_books(openid,content):
    data = Redis_chche(openid,None,None,"load")
    if data:
        try:
            retrieve_re= r"#(.*)"
            retrieve_result = re.search(retrieve_re,content)
            num = int(retrieve_result.group(1))

        except:
            msg = "图书收藏格式有误，请重新输入"
        else:
            data = eval(data)
            finaldata = data[num]
            sql = "select * from collect where openid = %s and bookid = %s"
            param = (openid,str(finaldata['bookid']))
            result = Connect_Database(sql,param,'select')
            if result == None:

                try:
                    # 存入数据库
                    sql = "insert into collect (openid,bookid,collect) values (%s,%s,%s)"
                    param = (openid,str(finaldata['bookid']),str(finaldata))
                    result = Connect_Database(sql,param,'commit')

                    if result == 'Success':
                        # 返回展示链接
                        msg = "以下图书已经添加进您的收藏夹，您可以随时点击菜单上的“我的收藏”按钮查看"
                        msg = msg + ( '\n\n'
                                      '书名： %s \n'
                                      '作者： %s \n'
                                      '出版社： %s \n'
                                      '索书号： %s \n'
                                      '文献类型： %s ')%( finaldata['title'],finaldata['author'],finaldata['publisher'],\
                                      finaldata['loc'],finaldata['types'] )

                except :
                    msg = "收藏图书时出错,可能您还未绑定学号，绑定后可实用收藏图书功能。"
            else:
                msg = "此图书已经收藏过，请不要重复收藏。"


    else:
        msg = "找不到上次的图书查询信息，请先查询后重试。"

    favorite = [
    {
        'title': u'图书收藏结果',
        'description': msg,
        'picurl': u'',
        'url': u'',
    }]
    return favorite

def Unfavorite_books(openid,content):

    try:
        retrieve_re= r"#(.*)"
        retrieve_result = re.search(retrieve_re,content)
        num = int(retrieve_result.group(1)) - 1

    except:
        msg = "图书收藏格式有误，请重新输入"
    else:
        try:
            sql = "select collect from collect where openid = (%s)"
            param = openid
            results = Connect_Database(sql,param,'selectall')
        except:
            msg = "您目前没有收藏的图书。"
        else:
            delbook = eval(results[num][0])

            sql = "delete from collect where openid = %s and bookid = %s"
            param = (openid,str(delbook['bookid']))
            result = Connect_Database(sql,param,'commit')

            msg = "以下图书已经从您的收藏夹移除。"
            msg = msg + ( '\n\n'
                          '书名： %s \n'
                          '作者： %s \n'
                          '出版社： %s \n'
                          '索书号： %s \n'
                          '文献类型： %s ')%( delbook['title'],delbook['author'],delbook['publisher'],\
                          delbook['loc'],delbook['types'] )

    favorite = [
    {
        'title': u'图书取消收藏结果',
        'description': msg,
        'picurl': u'',
        'url': u'',
    }]
    return favorite

#详情
def Detail_books(openid,content):
    data = Redis_chche(openid,None,None,"load")
    if data:
        try:
            retrieve_re= r"#(.*)"
            retrieve_result = re.search(retrieve_re,content)
            num = int(retrieve_result.group(1))
            data = eval(data)
            finaldata = data[num]
        except:
            msg = "图书详情格式有误，请重新输入"
        else:

            command_dict = {
                'type': "detail",
                'content': str(finaldata['bookid']),
                'library_url': library_url
            }

            try:
                compress_retrieve_page = Get_socket_server(str(command_dict))
                retrieve_page = str(decompress(compress_retrieve_page))
            except:
                msg = "暂时无法连接抓取服务器，请稍候再试"
            else:
                soup = BeautifulSoup(retrieve_page, "html.parser")
                try:
                    table = soup.find("table", {"width": "630"})
                    rows = (len(table.findAll('tr')))

                    dict_list = {}
                    i = 0
                    msg = '您要查询馆藏状态的图书：'

                    msg = msg + ( '\n\n'
                                  '书名： %s \n'
                                  '作者： %s \n'
                                  '出版社： %s \n'
                                  '文献类型： %s \n\n'
                                  '此图书馆藏状态：\n')%( finaldata['title'],finaldata['author'],finaldata['publisher'],\
                                  finaldata['types'] )

                    # set to run through rows
                    for row in table.findAll('tr')[1:min(rows,8)]:
                        col = row.findAll('td')
                        num = col[0].getText() #索书号
                        #code = col[1].getText() #条码号
                        #year = col[2].getText() #年卷期
                        loc = col[3].getText() #馆藏地
                        status = col[4].getText() #书刊状态

                        i = i + 1

                        dict_list[i] = { 'num':num,
                                         'loc':loc,
                                         'status':status }

                        msg = msg + ( '\n'
                                      '索书号 %s \n'
                                      '馆藏地 %s \n'
                                      '书刊状态 %s \n')%( num,loc,status )
                except:
                    msg = "图书馆藏状态分析出错"



    else:
        msg = "找不到上次的图书查询信息，请先查询后重试。"

    detail = [
    {
        'title': u'图书馆藏状态',
        'description': msg,
        'picurl': u'',
        'url': u'',
    }]
    return detail

#书评查询模块
def Evaluate_books(openid,content):
    data = Redis_chche(openid,None,None,"load")
    if data:
        try:
            retrieve_re= r"#(.*)"
            retrieve_result = re.search(retrieve_re,content)
            num = int(retrieve_result.group(1))
            data = eval(data)
            finaldata = data[num]
        except:
            msg = "豆瓣书评格式有误，请重新输入"
        else:

            command_dict = {
                'type': "detail",
                'content': str(finaldata['bookid']),
                'library_url': library_url
            }
            try:
                compress_retrieve_page = Get_socket_server(str(command_dict))
                retrieve_page = str(decompress(compress_retrieve_page))
                soup = BeautifulSoup(retrieve_page, "html.parser")


                msg = '您要查看豆瓣书评的图书：'

                msg = msg + ( '\n\n'
                              '书名： %s \n'
                              '作者： %s \n'
                              '出版社： %s \n'
                              '文献类型： %s \n\n'
                              '点击此卡片查看豆瓣书评\n')%( finaldata['title'],finaldata['author'],finaldata['publisher'],\
                              finaldata['types'] )

                ISBN_re = r'http://www.douban.com/isbn/(.*)/"><img src'
                ISBN_re = re.compile(ISBN_re)
                ISBN = ISBN_re.findall(retrieve_page)[0]
                ISBN = BeautifulSoup(ISBN, "html.parser")
                display_url = douban_url + str(ISBN)

            except:
                msg = "暂时无法连接抓取服务器，请稍候再试"

    else:
        msg = "找不到上次的图书查询信息，请先查询后重试。"

    detail = [
    {
        'title': u'豆瓣书评',
        'description': msg,
        'picurl': u'',
        'url': display_url,
    }]
    return detail


#返回图文信息
def news_return(title,description,picurl,url):

    news = [
    {
        'title': title,
        'description': description,
        'picurl': picurl,
        'url': url,
    }]

    return news


# 登陆h3c管理端
def Login_network():
    pass


# 获取网络状态
def Get_network_status():
    pass


# 设置网络暂停
def Get_network_offline():
    pass


# 验证码识别
def Captcha():
    pass
