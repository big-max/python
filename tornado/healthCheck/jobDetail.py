#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web
import json
import demjson
import os
import pdb
import re
from handler import proj_log
from db import mongoOps
import pymongo
import time
import base64
class JobDetailHandler(tornado.web.RequestHandler):
     @tornado.web.asynchronous
     def get(self):
         jobdetail_uuid=self.get_argument('jobDetail_uuid')
         cursor = mongoOps.db().healthJobDetails.find_one({'jobDetail_uuid':jobdetail_uuid},{'_id':0})
         self.write(cursor)
         self.finish()
   


     def getJobDetailList(self,jobuuid):
         out=[]  #change to array to printout
         res=mongoOps.db().healthJobDetails.find({'job_uuid':jobuuid},{'_id':0})
         for jobDetail in res:
             out.append(jobDetail)
         if len(out) == 0:
            self.write({'status':2,'msg':'no data found!'})
         elif len(out) > 0 :
            self.write({'status':1,'msg':out})
         else:
            self.write({'status':0,'msg':'faiulre'})
         self.finish()

     @tornado.web.asynchronous
     def post(self):
         proj_log.log().debug('JobDetailHandler::post 收到数据'+self.request.body)
         body = json.loads(self.request.body)
         self.getJobDetailList(body['job_uuid'])

