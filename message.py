# -*- coding: utf-8 -*-

# 获取最新校历
def Button_calender():

    xl = [
    {
        'title': u'最新校历',
        'description': u'2015-2016学年第二学期校历。点击查看',
        'picurl': u'http://mmbiz.qpic.cn/mmbiz/nXEKs550rhSry6bUTFN1ibpn0iaEfvtQCa6WEuSjdoFYz2P44gT7P5VcSvJEyRXCqaFgMj9YtrCzmdiaFkDktZbFA/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1',
        'url': u'http://mp.weixin.qq.com/s?__biz=MzI5NTE1MzkxNQ==&mid=543789917&idx=1&sn=4b807bb900775dc8568085129ece53de#rd',
    }]
    return xl


# 获取精彩活动
def Button_party():
    print "Click_party"
    party = [
    {
        'title': u'【排球战报】相识有缘，一网相连!',
        'description': u'',
        'picurl': u'http://news.myhbzs.cn/images/news-1-1.png',
        'url': u'http://mp.weixin.qq.com/s?__biz=MzA3MTYzNDcxNg==&mid=2699852896&idx=1&sn=e0dd59d6e8a337a966dafa709e422e8a&scene=0#wechat_redirect',
    },
    {
        'title': u'【海滨小当家】刀工大比拼！！',
        'description': u'',
        'picurl': u'http://news.myhbzs.cn/images/news-1-2.jpg',
        'url': u'http://mp.weixin.qq.com/s?__biz=MzA3MTYzNDcxNg==&mid=2699852896&idx=2&sn=250e4819e8e0bd8a5516af81ed2ea62b&scene=0#wechat_redirect',
    },
    {
        'title': u'【中国美】当代中国8大奇迹工程，你知道几个？',
        'description': u'',
        'picurl': u'http://news.myhbzs.cn/images/news-1-3.jpg',
        'url': u'http://mp.weixin.qq.com/s?__biz=MzA3MTYzNDcxNg==&mid=2699852896&idx=3&sn=e1d8fadd7a445f4fc3428196b2e6853e&scene=0#wechat_redirect',
    }]
    return party


# 获取教务通告
def Button_warn():
    print "Click_warn"
    warn = [
    {
        'title': u'教务公告',
        'description': u'好像最近没什么信息~',
        'picurl': u'http://news.myhbzs.cn/images/myhbzs_logo.png',
        'url': u'http://mp.weixin.qq.com/s?__biz=MzI5NTE1MzkxNQ==&mid=543789921&idx=1&sn=1de18a7dc97f59b59983aa2c5ddab710#rd',
    }]
    return warn


# 关注欢迎信息
def Subscribe_help():
    msg = ( '欢迎关注海滨学院非官方微信服务号\n\n'
            '使用教务查询功能请先绑定学号\n'
            '绑定方法：直接发送 “绑定#学号#密码”，例如发送“绑定#12111000#password”，'
            '提示绑定成功后即可；解绑请直接回复“解绑”\n\n'
            '使用图书馆图书查询功能，直接发送“图书馆#书名”，例如发送“图书馆#天使与魔鬼”，'
            '便可收到相关的图书信息及在图书馆中的位置\n\n'
            '更多功能正在规划和完善，感谢您的支持~ \n\n'
            '本助手核心功能依赖于校内服务，可能会出现不稳定等问题，为正常现象。'
            '没准等等就好了\n'
            '最后，有什么建议欢迎给我留言\n\("▔□▔)/  \n')

    subscribe = [
    {
        'title': u'欢迎关注我的海滨助手',
        'description': msg,
        'picurl': u'http://news.myhbzs.cn/images/myhbzs_logo.png',
        'url': u'http://myhbzs.cn/',
    }]
    return subscribe


# 未绑定信息
def Bind_help():
    help = ( '您还未绑定账号，请先绑定\n'
             '绑定方法： 发送“绑定#学号#密码”，例如“绑定#12111000#password”\n'
             '绑定成功后便可使用全部功能，如需解除绑定请回复 “解绑”')
    return help


# 绑定失效提醒
def Expired_help():
    help = ( '您绑定的账号信息可能已经失效，请解绑后重新绑定\n'
             '绑定方法： 发送“绑定#学号#密码”，例如“绑定#12111000#password”\n'
             '绑定成功后便可使用全部功能，如需解除绑定请回复 “解绑”')
    return help


# 帮助信息
def Button_help():
    msg =( '关于本助手：\n\n'
           '本系统为北京交通大学海滨学院非官方微信服务号，与学院无任何利益相关\n\n\n'
           '使用方法：\n\n'
           '使用教务查询功能请先绑定学号\n'
           '绑定方法：直接发送 “绑定#学号#密码”，例如发送“绑定#12111000#password”，'
           '提示绑定成功后即可；解绑请直接回复“解绑”\n\n'
           '使用图书馆图书查询功能，直接发送“图书馆#书名”，例如发送“图书馆#天使与魔鬼”，'
           '便可收到相关的图书信息及在图书馆中的位置\n\n'
           '更多功能正在规划和完善，感谢您的支持~ \n\n'
           '本助手核心功能依赖于校内服务，可能会出现不稳定等问题，为正常现象。'
           '没准等等就好了\n'
           '最后，有什么建议欢迎给我留言\n\("▔□▔)/  \n')

    help = [
    {
        'title': u'帮助信息',
        'description': msg,
        'picurl': u'',
        'url': u'http://myhbzs.cn/',
    }]
    return help
