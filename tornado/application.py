#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''
	@author:hujin
	@date:2016-3-2
	@desc:this file is used to instant Application 
'''
import url
import tornado.web
from tornado.options import define,options
settings={"debug":True}
#define("debug",default=True,help='Debug Mode',type=bool)
class application(tornado.web.Application):
    def __init__(self,handlers):
            tornado.web.Application.__init__(self, handlers)

#application=application(url.url,**settings)
application=application(url.url)
