#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.web
import tornado.ioloop
import pdb
import re
import json
from db import mongoOps
import pymongo

class HealthchecherrmsgHandler(tornado.web.RequestHandler):

   @tornado.web.asynchronous
   def get(self):
       uuid=self.get_argument("healthJobsRunResult_uuid",'withoutuuid')
       try:
         result=mongoOps.db().healthJobRunResult.find_one({'healthJobsRunResult_uuid':uuid},{'_id':0})
         if result:
            self.write({'errmsg':result['healthJobsRunResult_errmsg']}) 
         else:
            self.write({'errmsg':'没有找到本次任务的uuid!'})
       except KeyError as err:
            self.write({'errmsg':'错误描述未产生!'})
       self.finish()
             

