#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado.httpserver
import datetime
from db import mongoOps
from application import application				
from tornado.options import define,options
from handler.proj_log import log
define('port',default=8000,help='run on the given port',type=int)
from multiprocessing import cpu_count
def main():
    tornado.options.parse_command_line()
    http_server=tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    #http_server.bind(options.port)
    #http_server.start(num_processes=cpu_count())
    log().info('the server is running at http://127.0.0.1:%s/' %options.port)
    log().info('quit the server with Control-C')
    tornado.ioloop.IOLoop.instance().start()
if __name__ == "__main__":
    main()
