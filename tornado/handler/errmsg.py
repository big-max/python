#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.web
import tornado.ioloop
import pdb
import re
import json
from db import mongoOps
import pymongo

class errmsgHandler(tornado.web.RequestHandler):

      @tornado.web.asynchronous
      def get(self):
          uuid=self.get_argument("playbook_uuid",'withoutuuid')
          outMsg=None
          outErr=None
          outStd=None
          try:
             result=mongoOps.db().playbooks.find_one({'uuid':uuid},{'_id':0})          
             if result:
                 if result.has_key('msg'):
                    outMsg= result['msg']
                 else:
                    outMsg=" " 
                 if result.has_key('stdout'):
                    outStd=result['stdout']
                 else:
                    outStd=" "
                 if result.has_key('stderr'):
                    outErr=result['stderr']                    
                 else:
                    outErr=" " 
                 self.write({'errmsg':str(outMsg.encode('utf8'))+"\n"+str(outStd.encode('utf8'))+"\n"+str(outErr.encode('utf8'))}) 
             else:
                 self.write({'errmsg':'没有找到本次任务的uuid!'})
          except KeyError as err:
                self.write({'errmsg':'错误描述未产生!'})
          self.finish()
             

