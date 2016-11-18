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

class JobRunResultHandler(tornado.web.RequestHandler):
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
                jobDetail_uuid=self.get_argument("jobDetail_uuid")
                healthJobsRunResult_datetime=self.get_argument("healthJobsRunResult_datetime")
                if len(healthJobsRunResult_datetime) > 5 and jobDetail_uuid != None:
                   out=[]
                   result=mongoOps.db().healthJobRunResult.find({'jobDetail_uuid':jobDetail_uuid,'healthJobsRunResult_datetime':healthJobsRunResult_datetime},{'_id':0})
                   for res in result:
                       out.append(res)
                   self.write({'status':1,'msg':json.dumps(out)})
                   self.finish()
                elif jobDetail_uuid != None:
                   out=[]
                   #result=mongoOps.db().healthJobRunResult.find({'jobDetail_uuid':jobDetail_uuid},{'_id':0}).sort('healthJobsRunResult_datetime',pymongo.DESCENDING)
                   result=mongoOps.db().healthJobRunResult.find({'jobDetail_uuid':jobDetail_uuid},{'_id':0}).sort('healthJobsRunResult_datetime',pymongo.ASCENDING)
                   for res in result:
                       out.append(res)
                   self.write({'status':1,'msg':json.dumps(out)})
                   self.finish()
                    # find everyday job
                   
             if curPage =='summary':
                healthJobsRunResult_uuid=self.get_argument('healthJobsRunResult_uuid')
                if healthJobsRunResult_uuid != None:
                   out={}
                   result=mongoOps.db().healthJobRunResult.find_one({'healthJobsRunResult_uuid':healthJobsRunResult_uuid},{'_id':0})
                   self.write({'status':1,'msg':result})
                   self.finish()
 
