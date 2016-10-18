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
import uuid
import base64
import datetime
#from apscheduler.scheduler import Scheduler
from  proj  import tasks
from crontab import CronTab
class JobHandler(tornado.web.RequestHandler):
 
     @tornado.web.asynchronous         
     def get(self):
         cursor = mongoOps.db().healthJobs.find({},{'_id':0}).sort('job_scheduled_at',pymongo.DESCENDING)
         out=[]
         for res in cursor:
             out.append(res)
         self.write(json.dumps(out))
         self.finish()
          
     def getJobTargetIPList(self,jobType,jobTarget):
         #out=''
         if jobTarget == 'All':
 
            result=mongoOps.db().healthCheckGroups.find_one({'group':jobType.lower()},{'_id':0,'group':0})
            if result:
               out=''
               for res in result['iplist']:
                   out+=res+','
               return out
         else:
             return jobTarget 
            

         
     def run(self,jobuuid,jobType,jobTarget,jobSubmitedby,jobScheduleAt,job_lastrun_at,job_if_daily,job_groupOrIP):
         jobout={}
         jobout['job_uuid']=jobuuid
         jobout['job_type']=jobType
         _jobTarget=self.getJobTargetIPList(jobType,jobTarget)
         jobout['job_target']=_jobTarget
         jobout['job_submited_by']=jobSubmitedby 
         jobout['job_scheduled_at']=jobScheduleAt
         jobout['job_lastrun_at']=job_lastrun_at
         jobout['job_if_daily']=job_if_daily
         jobout['job_groupOrIP']=job_groupOrIP

         jobDetailOut={}
         jobDetail_uuid=uuid.uuid1()
         jobDetailOut['jobDetail_uuid']=str(jobDetail_uuid)
         jobDetailOut['jobDetail_scheduled_at']=jobScheduleAt
         jobDetailOut['jobDetail_status']=0
         jobDetailOut['jobDetail_submited_by']=jobSubmitedby
         jobDetailOut['job_uuid']=jobuuid
         jobDetailOut['jobDetail_target']=_jobTarget
         jobDetailOut['jobDetail_groupOrIP']=job_groupOrIP
         jobDetailOut['jobDetail_if_daily']=job_if_daily
         jobDetailOut['jobDetail_detail']='./healthCheck_outline.do?jobtype='+jobType+'&jobDetail_uuid='+str(jobDetail_uuid)
         jobout['job_detail']='./healthCheck_outline.do?jobtype='+jobType+'&jobDetail_uuid='+str(jobDetail_uuid)+'&healthJobsRunResult_datetime='+self.convertScheduledatDate(jobScheduleAt)
         try:         
            mongoOps.db().healthJobs.insert(jobout) 
            mongoOps.db().healthJobDetails.insert(jobDetailOut) 
            if job_if_daily == '0' or job_if_daily == '2':
               #tasks.healthCheck_run_playbook.delay(jobuuid,str(jobDetail_uuid),_jobTarget,jobType.lower()+'hc',self.convertScheduledatDate(jobScheduleAt),job_if_daily,jobScheduleAt)
               tasks.healthCheck_run_playbook.apply_async(args=[jobuuid,str(jobDetail_uuid),_jobTarget,jobType.lower()+'hc',self.convertScheduledatDate(jobScheduleAt),job_if_daily,jobScheduleAt],queue='queue_healthCheck_run_playbook')
            if job_if_daily == '1':
               target_datetime=jobScheduleAt+":00"       
               betweenSeconds=self.calTime(target_datetime) 
               tasks.healthCheck_run_playbook.apply_async((jobuuid,str(jobDetail_uuid),_jobTarget,jobType.lower()+'hc',self.convertScheduledatDate(jobScheduleAt),job_if_daily,jobScheduleAt),countdown=betweenSeconds)
 
         except Exception as e:
            raise e 
            return "error" 
         return True
    
     # date1 now    date2 target time 
     def calTime(self,date2):
         date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
         date1=time.strptime(date,"%Y-%m-%d %H:%M:%S")
         date2=time.strptime(date2,"%Y-%m-%d %H:%M:%S")
         date1=datetime.datetime(date1[0],date1[1],date1[2],date1[3],date1[4],date1[5])
         date2=datetime.datetime(date2[0],date2[1],date2[2],date2[3],date2[4],date2[5])
         return (date2-date1).seconds
     
     def createJob(self,job_param):
         job_uuid=job_param['job_uuid']
         #job_status=job_param['job_status']
         job_type=job_param['job_type']
         job_target=job_param['job_target']
         job_scheduled_at=job_param['job_scheduled_at']
         job_Submitedby=job_param['job_submited_by']
         job_lastrun_at=job_param['job_lastrun_at']
         job_if_daily=job_param['job_if_daily']
         job_runType = job_param['job_runType']
         job_groupOrIP = job_param['job_groupOrIP']
  #    if job_runType['status'] == 0 :   # 0   run immediately 1 run on time  2 run every datetime   
         retVal = self.run(job_uuid,job_type,job_target,job_Submitedby,job_scheduled_at,job_lastrun_at,job_if_daily,job_groupOrIP)
         if retVal == True:
            self.write({'status':1,'msg':'success'})
            self.finish()
         else:
            self.write({'status':0,'msg':retVal})
            self.finish()
       
     def deleteJob(self,job_param):
         cron = CronTab(user='root')   
         job_uuid=job_param['job_uuid']               
         jobuuids=job_uuid.split(',')
         for jobuuid in jobuuids:    #delete more
             mongoOps.db().healthJobs.remove({'job_uuid':jobuuid})
             mongoOps.db().healthJobDetails.remove({'job_uuid':jobuuid})
             mongoOps.db().healthJobRunResult.remove({'job_uuid':jobuuid})
             jobs=cron.find_command(jobuuid)  #find a job which to be deleted if run immediately not do
             for job in jobs:
                 cron.remove(job)
             cron.write(user='root')
         self.write({'status':1,'msg':'deleted '})
         self.finish()


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

     @tornado.web.asynchronous
     def post(self):
         proj_log.log().debug('JobHandler::post 收到数据'+self.request.body)
         body = json.loads(self.request.body)
         if body['operType']=='createJob':
            self.createJob(body)
         if body['operType'] == 'deleteJob':
            self.deleteJob(body)

