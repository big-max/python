#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web
import json
import os
import pdb
import re
from handler import proj_log
from db import mongoOps
import pymongo
import time
import uuid
import base64
import datetime

class configJobRunResultHandler(tornado.web.RequestHandler):
      @tornado.web.asynchronous
      def post(self):
          body=json.loads(self.request.body)
          runResult=body['healthJobsRunResult_uuid']
          res=mongoOps.db().healthJobRunResult.find_one({'healthJobsRunResult_uuid':runResult},{'_id':0})
          if body['product'] == 'os':
             summary_location=res['healthJobsRunResult_os_summary_loc']
          else:
             summary_location=res['healthJobsRunResult_summary_loc']
          buf_size=1000
          with open(summary_location,'rb') as f:
               while True:
                     data=f.read(buf_size)
                     if not data:
                        break
                     self.write(data)
          self.finish()

#上线到linux 修改
#      @tornado.web.asynchronous
#      def post1(self):
#          body=json.loads(self.request.body)
#          runResult=body['healthJobsRunResult_uuid']
#          res=mongoOps.db().healthJobRunResult.find_one({'healthJobsRunResult_uuid':runResult},\
#          {'_id':0})        
#          summary_location=res['healthJobsRunResult_summary_loc']
#          self.write({'fileaddr':summary_location})
#          self.finish()


      @tornado.web.asynchronous
      def get(self):
             curPage=self.get_argument('curPage')  #judge current page is which
             if curPage == 'outline':
                jobDetail_uuid=self.get_argument("confCompDetail_uuid")
                configJobsRunResult_datetime=self.get_argument("confCompRunResult_datetime")
                confCompDetail_if_daily=self.get_argument('confCompDetail_if_daily')
                if confCompDetail_if_daily == '0': # run immediately
                   out=[]
                   result=mongoOps.db().confCompRunResult.find({'confCompDetail_uuid':jobDetail_uuid,'confCompJobRunResult_datetime':configJobsRunResult_datetime},{'_id':0})
                   for res in result:
                       out.append(res)
                   self.write({'status':1,'msg':json.dumps(out)})
                   self.finish()
                elif confCompDetail_if_daily == '2':  # run every day
                   out=[]
             #      result=mongoOps.db().confCompRunResult.find({'confCompDetail_uuid':jobDetail_uuid,'confCompJobRunResult_datetime':configJobsRunResult_datetime},{'_id':0}).sort('confCompJobRunResult_datetime',pymongo.ASCENDING)
                   result=mongoOps.db().confCompRunResult.find({'confCompDetail_uuid':jobDetail_uuid},{'_id':0}).sort('confCompJobRunResult_datetime',pymongo.ASCENDING)
                   for res in result:
                       out.append(res)
                   self.write({'status':1,'msg':json.dumps(out)})
                   self.finish()
                   
             if curPage =='summary':
                confCompJobRunResult_uuid=self.get_argument('confCompJobRunResult_uuid')
                if confCompJobRunResult_uuid != None:
                   out={}
                   result=mongoOps.db().confCompRunResult.find_one({'confCompJobRunResult_uuid':confCompJobRunResult_uuid},{'_id':0})
                   self.write({'status':1,'msg':result})
                   self.finish()
 
