#!/usr/bin/env python
# -*- coding:utf-8 -*-

# #执行客户端发送过来的命令，并把执行结果返回给客户端
import sys
import SocketServer
from base import (Get_zfinfo,Retrieve_books)

reload(sys)
sys.setdefaultencoding("utf-8")

class MyTCPHandler(SocketServer.BaseRequestHandler):
    #继承BaseRequestHandler基类，然后必须重写handle方法，并且在handle方法里实现与客户端的所有交互

    def handle(self):
        print 'Client connect:', self.request.getpeername()
        while  True:
            command = self.request.recv(1024) #接收1024字节数据
            if not len(command):
                break
            print self.request.getpeername()[0] + ':' + str(command)

            #判断请求类型
            command = eval(command)
            if command['type'] == 'jw':
                results = Get_zfinfo(command['username'],command['password'],command['module'],command['jw_url'],command['now_year'],command['now_semester'])
            else :
                results = Retrieve_books(command['type'],command['content'],command['library_url'])

            self.request.sendall(results)

if __name__ == "__main__":
    HOST, PORT = '', 51888

    # 把刚才写的类当作一个参数传给ThreadingTCPServer这个类，下面的代码就创建了一个多线程socket server
    server = SocketServer.ThreadingTCPServer((HOST, PORT), MyTCPHandler)

    # 启动这个server,这个server会一直运行，除非按ctrl-C停止
    server.serve_forever()
