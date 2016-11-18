#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado.httpserver
from handler import proj_log
from db import mongoOps
import json
import demjson
import os
import pdb
import re
import pymongo
import time
import uuid
import base64
import datetime
from  proj  import tasks
  
class configConfHandler(tornado.web.RequestHandler):

      @tornado.web.asynchronous
      def post(self):
          result=mongoOps.db().confCompRunResult.distinct('confCompJobRunResult_ip')
          vers = json.dumps(result)
          self.write({'status':1,'msg':vers})
          self.finish()
  

      @tornado.web.asynchronous
      def get(self):
          out=[]
          ip=self.get_argument('ip')
          result=mongoOps.db().confCompRunResult.find({'confCompJobRunResult_ip':ip,'confCompJobRunResult_result':0},{'_id':0,'confCompJobRunResult_result':0,'confCompDetail_uuid':0,'confComp_uuid':0,'confCompJobRunResult_detail':0,'confCompJobRunResult_uuid':0})
          for res in result:
              if res.has_key('confCompRunResult_errmsg'):
                 continue
              elif res.has_key('confCompJobRunResult_retJson'):
                 out.append(res)
              else:
                 pass
          '''

          for res in result:
              retJsonstr=res['confCompJobRunResult_retJson']
              retJson=json.loads(retJsonstr)
              dic={}
              dic['product']=retJson['product']
              dic['datetime']=res['confCompJobRunResult_datetime']
              datas=retJson['data']
              for arr in datas:
          '''     
          '''
          for res in result:
              retJsonstr=res['confCompJobRunResult_retJson'] 
              retJson=json.loads(retJsonstr)
              dic={}
              #array=[]
              dic['ip']=ip
              dic['product']=retJson['product']
              dic['datetime']=res['confCompJobRunResult_datetime']
              innerArray = retJson['data']
              for arr in innerArray:
                  inner={}
                  inner['name']=arr['name']
                  inner['version']=arr['version']
                  inner['type']=arr['type']
              dic['proInfo']=inner
              out.append(dic)  
          '''
          retValue=json.dumps(out)
          self.write({'status':1,'msg':retValue})
          self.finish()
