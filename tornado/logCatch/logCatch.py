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
import pdb

class logCatchHandler(tornado.web.RequestHandler):
      @tornado.web.asynchronous
      def get(self):
          out=[]
          result=mongoOps.db().logCatch.find()
          for res in result:
              out.append(res)
          print json.dumps(out)
          self.write(json.dumps(out))
          self.finish()
      
      def deleteLog(self,body):
          try:
             log_uuid=body['log_uuid']
             loguuids = log_uuid.split(',') 
             for uuid in loguuids:
                 mongoOps.db().logCatch.remove({'_id':uuid})         
             self.write({'status':1,'msg':'delete success'})
          except Exception as e:
             self.write({'status':0,'msg':'delete failed'})
          self.finish() 
            
        
       
      @tornado.web.asynchronous
      def post(self):
          proj_log.log().info(self.request.body)
          body=json.loads(self.request.body)
          if body.has_key('operType') and body['operType']=='deleteLog':
             self.deleteLog(body)
          else:
             self.addLog(body)

      def addLog(self,body):
          proj_log.log().info(self.request.body)
          body=json.loads(self.request.body)
          ip=body['ip']
          product=body['product']
          version=body['version']
          task_timestamp=body['task_timestamp']
          instance=body['instance']
          job={}
          job['ip']=ip
          job['product']=product
          job['version']=version
          job['task_timestamp']=task_timestamp
          job['instance']=instance 
          uuid1=str(uuid.uuid1())
          job['_id']=uuid1
          mongoOps.db().logCatch.insert(job)
          tasks.logCatch_run_playbook.apply_async(args=[uuid1,ip,product,instance,task_timestamp],queue='queue_logCatch_run_playbook')
          self.write({'status':1,'msg':'success'})
          self.finish() 



