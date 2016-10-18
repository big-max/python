#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web
import json
import demjson
import subprocess
import os
import pdb
import re
from proj_log import log

#加上IP地址有效性判断
class hdisksHandler(tornado.web.RequestHandler):
      @tornado.web.asynchronous
      def get(self):
          log().debug('DB2VG::get 收到数据')
          try:
             ip=self.get_argument('ip')
             param='/usr/bin/ansible ' + ip + ' -i ' + ip+', -m get_hdisks'
             retVal=subprocess.Popen([param],shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
             (stdout,stderr)=retVal.communicate()
             first=stdout.index('{')
             last=stdout.rindex('}')
             ansi_obj=json.loads(stdout[first:last+1])
             self.write({'hdisks':ansi_obj['module_stdout']})
             self.finish()
          except Exception:
             self.write([])
             self.finish()
         


