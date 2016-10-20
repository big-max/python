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
from crontab import CronTab

class ConfigJobHandler(tornado.web.RequestHandler):
      #   2016-07-08 15:21    to   201607081521
     def convertScheduledatDatetimeDate(self,date):
         tempDate=datetime.datetime.strptime(date,'%Y-%m-%d %H:%M')
         return datetime.datetime.strftime(tempDate,'%Y%m%d%H%M')

     # 08:30    translate to 0830
     # 2016/07/08 15:21:12   translate to 201607081521    
     def convertScheduledatDate(self,date):
         if len(date)>5:
            tempDate=datetime.datetime.strptime(date,'%Y-%m-%d %H:%M')
            return datetime.datetime.strftime(tempDate,'%Y%m%d%H%M')
         else:
            tempDate=datetime.datetime.strptime(date,'%H:%M')
            return datetime.datetime.strftime(tempDate,'%H%M')

     def getJobTargetIPList(self,jobType,jobTarget):
         if jobTarget == 'All':
            result=mongoOps.db().healthCheckGroups.find_one({'group':jobType.lower()},{'_id':0,'group':0})      
            if result:
               out=''
               for res in result['iplist']:
                   out+=res+','
               return out
         else:
            return jobTarget

     def createJob(self,confComp_param):
         confComp_uuid=confComp_param['confComp_uuid']
         confComp_type=confComp_param['confComp_type']
         confComp_target=confComp_param['confComp_target']
         confComp_scheduled_at=confComp_param['confComp_scheduled_at']
         confComp_Submitedby=confComp_param['confComp_submited_by']
         confComp_lastrun_at=confComp_param['confComp_lastrun_at']
         confComp_if_daily=confComp_param['confComp_if_daily']
         confComp_runType = confComp_param['confComp_runType']
         confComp_groupOrIP = confComp_param['confComp_groupOrIP']
         confComp_userName=confComp_param['userName']
         retVal = self.run(confComp_uuid,confComp_type,confComp_target,confComp_Submitedby,confComp_scheduled_at,confComp_lastrun_at,confComp_if_daily,confComp_groupOrIP,confComp_userName)   
         if retVal == True:
            self.write({'status':1,'msg':'success'})
            self.finish()
         else:
            self.write({'status':0,'msg':retVal})
            self.finish()
                 
     def run(self,jobuuid,jobType,jobTarget,jobSubmitedby,jobScheduleAt,job_lastrun_at,job_if_daily,job_groupOrIP,userName):        
         jobout={}
         jobout['confComp_uuid']=jobuuid
         jobout['confComp_type']=jobType
         _jobTarget=self.getJobTargetIPList(jobType,jobTarget)
         jobout['confComp_target']=_jobTarget
         jobout['confComp_submited_by']=jobSubmitedby
         jobout['confComp_scheduled_at']=jobScheduleAt
         jobout['confComp_lastrun_at']=job_lastrun_at
         jobout['confComp_if_daily']=job_if_daily
         jobout['confComp_groupOrIP']=job_groupOrIP

         jobDetailOut={}
         jobDetail_uuid=uuid.uuid1()
         jobDetailOut['confCompDetail_uuid']=str(jobDetail_uuid)
         jobDetailOut['confCompDetail_scheduled_at']=jobScheduleAt
         jobDetailOut['confCompDetail_status']=0
         jobDetailOut['confCompDetail_submited_by']=jobSubmitedby
         jobDetailOut['confComp_uuid']=jobuuid
         jobDetailOut['confCompDetail_target']=_jobTarget
         jobDetailOut['confCompDetail_groupOrIP']=job_groupOrIP
         jobDetailOut['confCompDetail_if_daily']=job_if_daily
         jobDetailOut['confCompDetail_detail']='./configCompare_outline.do?confComptype='+jobType+'&confCompDetail_uuid='+str(jobDetail_uuid) 
         jobout['confComp_detail']='./configCompare_outline.do?confComptype='+jobType+'&confCompDetail_uuid='+str(jobDetail_uuid)+'&confCompDetail_if_daily='+job_if_daily+'&confCompRunResult_datetime='+self.convertScheduledatDate(jobScheduleAt) 
         try:
            mongoOps.db().confCompJobs.insert(jobout)
            mongoOps.db().confCompJobDetails.insert(jobDetailOut)
            if job_if_daily == '0' or job_if_daily == '2':
               tasks.configCompare_run_playbook.apply_async(args=[jobuuid,str(jobDetail_uuid),_jobTarget,jobType.lower()+'cc',self.convertScheduledatDate(jobScheduleAt),job_if_daily,jobScheduleAt,userName],queue='queue_configCompare_run_playbook')     
         except Exception as e:
            raise e
            return "error"
         return True

       


     @tornado.web.asynchronous
     def get(self):
       cursor = mongoOps.db().confCompJobs.find({},{'_id':0}).sort('confComp_scheduled_at',pymongo.DESCENDING)
       out=[]
       for res in cursor:
           out.append(res)
       self.write(json.dumps(out))
       self.finish()
    
     def deleteJob(self,job_param):
         try:
            userName = job_param['userName']
            cron = CronTab(user=userName)
            job_uuid=job_param['job_uuid']
            jobuuids=job_uuid.split(',')
            for jobuuid in jobuuids:    #delete more
                mongoOps.db().confCompJobs.remove({'confComp_uuid':jobuuid})
                mongoOps.db().confCompJobDetails.remove({'confComp_uuid':jobuuid})
                mongoOps.db().confCompRunResult.remove({'confComp_uuid':jobuuid})
                jobs=cron.find_command(jobuuid)#finda job which to be deleted if run immediately not do
                for job in jobs:
                    cron.remove(job)
                    cron.write(user=userName)
            self.write({'status':1,'msg':'deleted '})
         except Exception as e:
            self.write({'status':0,'msg':str(e)})
         self.finish()         

     @tornado.web.asynchronous
     def post(self):
         proj_log.log().debug('ConfigJobHandler::post 收到数据'+self.request.body)
         body = json.loads(self.request.body)
         if body['operType']=='createCfgCompJob':
            self.createJob(body)
         if body['operType'] == 'deleteCfgCompJob':
            self.deleteJob(body) 

