# -*- coding: utf-8 -*-
import json
import urllib
import urllib2
import StringIO
from basic import *
from message import *
import ConfigParser

# 读取配置文件
config = ConfigParser.ConfigParser()
config.read('config.conf')

display_url = config.get("display","display")

# 获取最新校历
def Click_calender():
    print "Click_calender"
    return Button_calender()

# 获取精彩活动
def Click_party():
    print "Click_party"
    return Button_party()

# 获取教务通告
def Click_warn():
    print "Click_warn"
    return Button_warn()

# 获取用户课程表
def Click_zf_schedule(openid):
    print "Click_zf_schedule"

    reply_title = "本学期课程安排"
    reply_msg = None
    reply_url = None

    user = Get_userinfo(openid)
    if (user == None):
        reply_title = "请先绑定学号"
        reply_msg = Bind_help()
    else:
        command_dict = {
            'type': 'jw',
            'username': user['username'],
            'password': user['password'],
            'module': 'N121603',
            'jw_url': jw_url,
            'now_year': now_year,
            'now_semester': now_semester
        }
        print str(command_dict)
        compress_result = Get_socket_server(str(command_dict))
        try:
            result = str(decompress(compress_result))
            soup = BeautifulSoup(result, "html.parser")

            #soup = Get_zfinfo(user['username'],user['password'],'N121603')

            if soup == None:
                reply_title = "绑定学号已失效"
                reply_msg = Expired_help()
            else:
                try:
                    table = soup.find("table", {"id": "Table1"})
                    rows = (len(table.findAll('td')) - 1)

                    dict_list = {}
                    line = 2
                    # set to run through x
                    for row in table.findAll('tr')[2:rows]:
                        col = row.findAll('td')
                        if line == 2 or line == 6 or line == 10:
                            date = col[0].getText('<br/>','<br/>') #上午、下午、晚上
                            classs = col[1].getText('<br/>','<br/>') #课程节数
                            mon= col[2].getText('<br/>','<br/>') #星期一
                            tues = col[3].getText('<br/>','<br/>')
                            wed = col[4].getText('<br/>','<br/>')
                            thur = col[5].getText('<br/>','<br/>')
                            fri = col[6].getText('<br/>','<br/>')
                            sat = col[7].getText('<br/>','<br/>')
                            sun = col[8].getText('<br/>','<br/>')

                        elif line == 4 or line == 8:
                            classs = col[0].getText('<br/>','<br/>') #课程节数
                            mon= col[1].getText('<br/>','<br/>') #星期一
                            tues = col[2].getText('<br/>','<br/>')
                            wed = col[3].getText('<br/>','<br/>')
                            thur = col[4].getText('<br/>','<br/>')
                            fri = col[5].getText('<br/>','<br/>')
                            sat = col[6].getText('<br/>','<br/>')
                            sun = col[7].getText('<br/>','<br/>')
                        else:
                            classs = None
                            mon= None
                            tues = None
                            wed = None
                            thur = None
                            fri = None
                            sat = None
                            sun = None

                        #此处以line-2 代替从0开始的i
                        dict_list[line-2] = { 'classs':classs,
                                         'mon':mon,
                                         'tues':tues,
                                         'wed':wed,
                                         'thur':thur,
                                         'fri':fri,
                                         'sat':sat,
                                         'sun':sun }

                        line = line + 1
                    #print dict_list
                    try:
                        table2 = soup.find("table", {"id": "DBGrid"})
                        rows2 = (len(table2.findAll('tr')) - 1)

                        dict_list2 = {}
                        i = 0
                        # set to run through rows
                        for row in table2.findAll('tr')[1:rows2]:
                            col = row.findAll('td')
                            course_num = col[0].getText() #课程编号
                            course = col[1].getText() #课程名称
                            old_date = col[2].getText() #原上课时间地点教师
                            new_date = col[3].getText() #现上课时间地点教师
                            time = col[4].getText() #申请时间

                            dict_list2[i] = { 'course_num':course_num,
                                             'course':course,
                                             'old_date':old_date,
                                             'new_date':new_date,
                                             'time':time }
                            i = i + 1
                    except:
                        dict_list2 = None
                    #print dict_list2
                    # 存入数据库
                    sql = "insert into schedule (openid,schedule,modify) values (%s,%s,%s) on duplicate key update schedule=%s,modify=%s"
                    param = (openid,str(dict_list),str(dict_list2),str(dict_list),str(dict_list2))

                    result = Connect_Database(sql,param,'commit')

                    #print result
                    if result == 'Success':
                        # 返回展示链接
                        reply_msg = ("本学期的课程安排已查询完毕，请点击此卡片查看\n"
                                     "（本课表信息可能存在遗漏，如在第2、4、6、8、10节开始的课程不能被获取"
                                     "此功能后期根据情况完善或删除）")

                        module_display_url = '/schedule/openid=%s&value=%s'%(openid,Md5(user['value']))
                        reply_url = display_url + module_display_url

                        #content = "<a href='%s%s'>点击此处查看详细课表</a>"%(display_url,module_display_url)
                        #print  content.encode("utf-8")

                        #return content
                    else :
                        reply_msg = "储存课表数据时出错"
                except:
                    reply_msg = "课表分析出错，暂不兼容此类型课表"
        except:
            reply_msg = "暂时无法连接抓取服务器，请稍候再试"
    schedule_message = [
    {
        'title': reply_title,
        'description': reply_msg,
        'picurl': u'',
        'url': reply_url,
    }]
    return schedule_message


# 获取用户成绩单
def Click_zf_score(openid):
    print "Click_zf_score"

    reply_title = "本学期考试成绩"
    reply_msg = None
    reply_url = None

    user = Get_userinfo(openid)
    if (user == None):
        reply_title = "请先绑定学号"
        reply_msg = Bind_help()
    else:

        command_dict = {
            'type': 'jw',
            'username': user['username'],
            'password': user['password'],
            'module': 'N121605',
            'jw_url': jw_url,
            'now_year': now_year,
            'now_semester': now_semester
        }
        print str(command_dict)
        compress_result = Get_socket_server(str(command_dict))
        try:
            result = str(decompress(compress_result))
            soup = BeautifulSoup(result, "html.parser")
            #soup = Get_zfinfo(user['username'],user['password'],'N121605')

            if soup == None:
                reply_title = "绑定学号已失效"
                reply_msg = Expired_help()
            else:
                table = soup.find("table", {"id": "Datagrid1"})
                rows = (len(table.findAll('tr')) - 1)

                dict_list = {}
                i = 0
                # set to run through rows

                for row in table.findAll('tr')[1:rows]:
                    col = row.findAll('td')
                    year = col[0].getText() #学年
                    semester = col[1].getText() #学期
                    #course_cod = col[2].getText() #课程代码
                    course = col[3].getText() #课程名称
                    course_character = col[4].getText() #课程性质
                    #course_belong = col[5].getText() #课程归属
                    credit = col[6].getText() #学分
                    point = col[7].getText() #绩点
                    score = col[8].getText() #成绩
                    minor_marks = col[9].getText() #辅修标记
                    makeup_score = col[10].getText() #补考成绩
                    rebuild_score = col[11].getText() #重修成绩
                    college = col[12].getText() #开课学院
                    remark = col[13].getText() #备注
                    rebuild_marks = col[14].getText() #重修标记


                    dict_list[i] = { 'year':year,
                                     'semester':semester,
                                     'course':course,
                                     'course_character':course_character,
                                     'credit':credit,
                                     'point':point,
                                     'score':score,
                                     'minor_marks':minor_marks,
                                     'makeup_score':makeup_score,
                                     'rebuild_score':rebuild_score,
                                     'college':college,
                                     'remark':remark,
                                     'rebuild_marks':rebuild_marks }

                    i = i + 1

                #print dict_list #字典手动检查
                if dict_list:
                    # 存入数据库
                    sql = "insert into score (openid,score) values (%s,%s) on duplicate key update score=%s"
                    param = (openid,str(dict_list),str(dict_list))

                    result = Connect_Database(sql,param,'commit')

                    #print result
                    if result == 'Success':
                        # 返回展示链接
                        reply_msg = "本学期的考试成绩已查询完毕，请点击此卡片查看"

                        module_display_url = '/score/openid=%s&value=%s'%(openid,Md5(user['value']))
                        reply_url = display_url + module_display_url


                        #content = "<a href='%s%s'>点击此处查看考试成绩</a>"%(display_url,module_display_url)

                        #print  content.encode("utf-8")

                        #return content
                    else :
                        reply_msg = "储存考试成绩数据时出错"
                else:
                    reply_msg = "本学期考试成绩数据为空，可能暂时未公布任何成绩信息，可以尽情玩耍啦~ \n (#￣▽￣#)"

        except:
            reply_msg = "暂时无法连接抓取服务器，请稍候再试"
    score_message = [
    {
        'title': reply_title,
        'description': reply_msg,
        'picurl': u'',
        'url': reply_url,
    }]
    return score_message




# 获取用户考试安排
def Click_zf_exam(openid):
    print "Click_zf_exam"

    reply_title = "本学期考试安排"
    reply_msg = None
    reply_url = None

    user = Get_userinfo(openid)
    if (user == None):
        reply_title = "请先绑定学号"
        reply_msg = Bind_help()
    else:
        command_dict = {
            'type': 'jw',
            'username': user['username'],
            'password': user['password'],
            'module': 'N121604',
            'jw_url': jw_url,
            'now_year': now_year,
            'now_semester': now_semester
        }
        print str(command_dict)
        compress_result = Get_socket_server(str(command_dict))
        try:
            result = str(decompress(compress_result))
            soup = BeautifulSoup(result, "html.parser")

            #soup = Get_zfinfo(user['username'],user['password'],'N121604')

            if soup == None:
                reply_title = "绑定学号已失效"
                reply_msg = Expired_help()
            else:
                table = soup.find("table", {"id": "DataGrid1"})
                #table = soup.find("table")
                rows = (len(table.findAll('tr')) - 1)

                dict_list = {}
                i = 0
                # set to run through rows
                for row in table.findAll('tr')[1:rows]:
                    col = row.findAll('td')
                    #course_num = col[0].getText() #课程课号
                    course = col[1].getText() #课程名称
                    name = col[2].getText() #姓名
                    date = col[3].getText() #考试时间
                    loc = col[4].getText() #考试地点
                    #form = col[5].getText() #考试形式
                    seat = col[6].getText() #座位号
                    #campus = col[7].getText() #校区

                    dict_list[i] = { 'course':course,
                                     'name':name,
                                     'date':date,
                                     'loc':loc,
                                     'seat':seat }
                    i = i + 1

                #print dict_list #字典手动检查

                if dict_list:
                    # 存入数据库
                    sql = "insert into exam (openid,exam) values (%s,%s) on duplicate key update exam=%s"
                    param = (openid,str(dict_list),str(dict_list))

                    result = Connect_Database(sql,param,'commit')


                    if result == 'Success':
                        # 返回展示链接
                        reply_msg = "本学期的考试安排已查询完毕，请点击此卡片查看"

                        module_display_url = '/exam/openid=%s&value=%s'%(openid,Md5(user['value']))
                        reply_url = display_url + module_display_url



                        #content = "<a href='%s%s'>点击此处查看考试安排</a>"%(display_url,module_display_url)

                        #print  content.encode("utf-8")
                        #return content
                    else :
                        reply_msg = "储存考试安排数据时出错"
                else:
                    reply_msg = "考试安排数据为空，可能近期并未安排考试，可以尽情玩耍啦~ \n (#￣▽￣#)"
        except:
            reply_msg = "暂时无法连接抓取服务器，请稍候再试"
    exam_message = [
    {
        'title': reply_title,
        'description': reply_msg,
        'picurl': u'',
        'url': reply_url,
    }]
    return exam_message

# 获取用户绑定状态
def Click_zf_userinfo(openid):
    print "Click_zf_userinfo"
    user = Get_userinfo(openid)
    if (user == None):
        reply_msg = Bind_help()
    else:
        command_dict = {
            'type': 'jw',
            'username': user['username'],
            'password': user['password'],
            'module': 'login',
            'jw_url': jw_url,
            'now_year': now_year,
            'now_semester': now_semester
        }
        print str(command_dict)
        try:
            Sname = Get_socket_server(str(command_dict))

            #Sname = Get_zfinfo(user['username'],user['password'],'login')
        except:
            reply_msg = "暂时无法连接绑定服务器，请稍候再试"
        else:
            if len(Sname) == 0:
                reply_msg = Expired_help()
            else:
                reply_msg = ("%s同学，您的帐号状态正常\n"
                             "您绑定的学号为%s\n"
                             "如需解绑请回复 “解绑”")%(Sname,user['username'])

    userinfo_message = [
    {
        'title': u'账户绑定状态',
        'description': reply_msg,
        'picurl': u'',
        'url': u'',
    }]
    return userinfo_message


# 校园网状态
def Click_network_status():
    print "Click_network_status"
    return '校园网功能正在开发中，开发完成后会通知大家~~~/飞吻'


# 校园网暂停
def Click_network_offline():
    print "Click_network_offline"
    return '校园网功能正在开发中，开发完成后会通知大家~~~/飞吻'


# 天气信息
def Click_weather():
    print "Click_weather"
    weatherurl ='http://weather.123.duba.net/static/weather_info/101090713.html'
    getweather = urllib2.urlopen(weatherurl).read()
    getweather=getweather[17:-1]
    loadweather = json.loads(getweather)['weatherinfo']
    loaddate = json.loads(getweather)['update_time']
    reply_msg = ('城市： %s \n'
                 '温度： %s℃\n'
                 '天气： %s\n'
                 '风向： %s\n'
                 '风力： %s\n'
                 'PM2.5指数： %s\n'
                 'PM2.5级别： %s\n'
                 '更新时间： %s')%( loadweather ['city'],
                                   loadweather ['temp'],
                                   loadweather ['img_title_single'],
                                   loadweather ['wd'],
                                   loadweather ['ws'],
                                   loadweather ['pm'],
                                   loadweather ['pm-level'],
                                   loaddate )
    weather = [
    {
        'title': u'黄骅实时天气',
        'description': reply_msg,
        'picurl': u'',
        'url': u'http://www.weather.com.cn/weather/101090713.shtml',
    }]
    return weather

# 获取用户收藏列表
def Click_collect(openid):
    print "Click_collect"
    sql = "select collect from collect where openid = (%s)"
    param = openid

    results = Connect_Database(sql,param,'selectall')
    i = 0
    if results:
        msg = '以下是您收藏的图书信息：'
        for row in results[0:min(len(results),7)]:
            book = eval(row[0])
            i = i + 1
            msg = msg + ( '\n\n'
                          '序号： %s \n'
                          '书名： %s \n'
                          '作者： %s \n'
                          '出版社： %s \n'
                          '索书号： %s \n'
                          '文献类型： %s ')%( i,book['title'],book['author'],book['publisher'],book['loc'],book['types'] )
    else:
        msg = "您的收藏列表为空。"

    collect_list = [
    {
        'title': u'图书收藏列表',
        'description': msg,
        'picurl': u'',
        'url': u'',
    }]

    return collect_list

# 帮助信息
def Click_help():
    print "Click_help"
    return Button_help()
