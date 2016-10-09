# -*- coding: utf-8 -*-
import re
#import json
import zlib
import urllib
import urllib2
import hashlib
import cookielib
from bs4 import BeautifulSoup
#import codecs


# 正方登陆
def Get_zfinfo(username,password,module,jw_url,now_year,now_semester):
    #try:
        #print "IN"
        loginURL = jw_url+'/default6.aspx'      #免验证码登录页

        page = urllib2.urlopen(loginURL).read()
        view = r'name="__VIEWSTATE" value="(.+)" '
        view = re.compile(view)
        finaview = view.findall(page)[0]

        postdata = urllib.urlencode({
            '__VIEWSTATE':finaview,
            'txtYhm':username,# 学号
            'txtMm':password,# 密码
            'rblJs':'学生',
            'btnDl':' 登录'})
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'
            }
        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        login_request = urllib2.Request(loginURL, postdata,headers)
        loginPage = opener.open(login_request).read()
        page =  unicode(loginPage, 'gb2312').encode("utf-8")
        #print page
        Sname = r'<span id="xhxm">(.+)同学</span>'
        Sname = re.compile(Sname)
        try:
            std_name = Sname.findall(page)[0]
            #print module
            if module == 'login':
                print "Query std_name Success \n"
                print std_name
                return std_name
            else:
                 # 获取Cookie
                for i in cookie:
                    Cookie = i.name+"="+i.value

                #print Cookie
                head = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Cache-Control':'no-cache',
                    'Connection':'keep-alive',
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Host':jw_url[7:],
                    'Cookie':Cookie,
                    'Origin':jw_url,
                    'Pragma':'no-cache',
                    'Referer':jw_url+'/xs_main.aspx?xh='+username,
                    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'
                    }

                getdata = urllib.urlencode({
                        'xh':username,
                        'xm':std_name,
                        'gnmkdm': module
                        })
                data = None
                #print std_name

                if module == 'N121603': #课表模块及链接
                    module_url = '/xskbcx.aspx?'

                elif module == 'N121604': #考试模块及链接
                    module_url = '/xskscx.aspx?'

                elif module == 'N121605' : #成绩模块及链接
                    module_url = '/xscjcx.aspx?'
                    jw_request= urllib2.Request(jw_url + module_url + getdata, None, head)     #发送请求得到含有数据页面
                    loginPage = unicode(opener.open(jw_request).read(), 'gb2312').encode("utf-8")
                    loginview = r'name="__VIEWSTATE" value="(.+)" '
                    loginview = re.compile(loginview)
                    loginfinaview = loginview.findall(loginPage)[0]
                    data = urllib.urlencode({
                        "__VIEWSTATE":loginfinaview,
                        "ddlXN":now_year,
                        "ddlXQ":now_semester,
                        "ddl_kcxz":'',
                        "btn_xq":'学期成绩'
                        })
                else:
                    return None


                jw_request= urllib2.Request(jw_url + module_url + getdata, data, head)     #发送请求得到含有数据页面
                result = unicode(opener.open(jw_request).read(), 'gb2312').encode("utf-8")
                #soup = BeautifulSoup(result, "html.parser")
                print "Query JW(%s) Success"%module

                print 'Before compression:',len(result.encode("utf-8"))
                compress_result = zlib.compress(result, zlib.Z_BEST_COMPRESSION)
                print 'After compression:',len(compress_result),'\n'
                return compress_result

        except:
            return None


    #except:
    #    return None


# 检索图书（抓取端处理数据）
def Retrieve_books2(title,library_url):
    try:

        retrieve_url = library_url + '/opac/openlink.php?historyCount=1&strText=' + title.encode("utf-8") + '&doctype=ALL&strSearchType=title&match_flag=forward&displaypg=20&sort=CATA_DATE&orderby=desc&showmode=table&location=ALL'
        #print retrieve_url
        retrieve_page = urllib2.urlopen(retrieve_url).read()

        soup = BeautifulSoup(retrieve_page, "html.parser")
        try:
            table = soup.find("table", {"id": "result_content"})
            rows = (len(table.findAll('tr')))

            i = 0
            msg = '以下是查询到的图书信息：'
            # set to run through rows
            for row in table.findAll('tr')[1:min(rows,8)]:
                col = row.findAll('td')
                num = col[0].getText() #序号
                title = col[1].getText() #书名
                author = col[2].getText() #作者
                publisher = col[3].getText() #出版信息
                loc = col[4].getText() #索书号
                types = col[5].getText() #文献类型

                i = i + 1
                msg = msg + ( '\n\n'
                              '书名： %s \n'
                              '作者： %s \n'
                              '出版社： %s \n'
                              '索书号： %s \n'
                              '文献类型： %s ')%( title,author,publisher,loc,types )

            if len(msg.encode("utf-8")) > 2048 :
                msg = '获取到的数据过长，无法显示。\n此情况属于微信接口限制，正在努力优化，请谅解。'
        except:
            msg = '很抱歉，没有找到您需要的图书信息。'


        return msg

    except:
        return "图书查询格式有误，请重新输入"

# 检索图书
def Retrieve_books_backup(title,library_url):
    try:
        retrieve_url = library_url + '/opac/openlink.php?historyCount=1&strText=' + title.encode("utf-8") + '&doctype=ALL&strSearchType=title&match_flag=forward&displaypg=20&sort=CATA_DATE&orderby=desc&showmode=table&location=ALL'
        #print retrieve_url
        retrieve_page = urllib2.urlopen(retrieve_url).read()
        print "Query Library Success"
        print 'Before compression:',len(retrieve_page.encode("utf-8"))
        compress_retrieve_page = zlib.compress(retrieve_page, zlib.Z_BEST_COMPRESSION)
        print 'After compression:',len(compress_retrieve_page),'\n'
        return compress_retrieve_page
    except:
        return None

# 检索图书
def Retrieve_books(types,content,library_url):
    try:
        if types == "detail":
            retrieve_url = library_url + '/opac/item.php?marc_no=' + content.encode("utf-8")
        elif types == "title" or types == "author":
            retrieve_url = library_url + '/opac/openlink.php?historyCount=1&strText=' + content.encode("utf-8") + '&doctype=ALL&strSearchType=' + types.encode("utf-8") + '&match_flag=forward&displaypg=20&sort=CATA_DATE&orderby=desc&showmode=table&location=ALL'
        else:
            retrieve_url = None
        #print retrieve_url
        retrieve_page = urllib2.urlopen(retrieve_url).read()
        print "Query Library Success"
        print 'Before compression:',len(retrieve_page.encode("utf-8"))
        compress_retrieve_page = zlib.compress(retrieve_page, zlib.Z_BEST_COMPRESSION)
        print 'After compression:',len(compress_retrieve_page),'\n'
        return compress_retrieve_page
    except:
        return None
