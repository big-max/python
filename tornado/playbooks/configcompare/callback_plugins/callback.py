import os
import time
import json
import pdb
import datetime
import uuid
from pymongo import MongoClient
from ansible.plugins.callback import CallbackBase
#coding=utf8
TIME_FORMAT='%Y-%m-%d %H:%M:%S'
status_code={'ok':1,'failed':2}
mongoinfo = {"host":"127.0.0.1","port":"27017","user":"","password":"","dbname":"ams"}

class CallbackModule(CallbackBase):
  def __init__(self):
        self.confCompDetail_uuid=None
        self.confComp_uuid=None
        self.ymlName=None
        self.task_timestamp=None
        self.confCompDetail_if_daily=None

  def db(self):
        dbhost = mongoinfo['host']
	dbport = mongoinfo['port']
	dbuser = mongoinfo['user']
	dbpwd  = mongoinfo['password']
	dbname = mongoinfo['dbname']
	uri = 'mongodb://%s:%s'%(dbhost,dbport)
	client = MongoClient(uri)
	db = client.ams 
	return db
        
  def v2_playbook_on_start(self, playbook):
      self.confCompDetail_uuid=playbook._entries[0]._variable_manager.extra_vars['confCompDetail_uuid']
      self.confComp_uuid=playbook._entries[0]._variable_manager.extra_vars['confComp_uuid']
      self.ymlName=playbook._entries[0]._variable_manager.extra_vars['ymlName']
      self.task_timestamp=playbook._entries[0]._variable_manager.extra_vars['task_timestamp']
      self.confCompDetail_if_daily=playbook._entries[0]._variable_manager.extra_vars['confCompDetail_if_daily']
      if self.confCompDetail_if_daily == '2': # run immediately
         curDatetime=datetime.datetime.now().strftime('%Y%m%d')
         self.task_timestamp = str(curDatetime) + str(self.task_timestamp)
         s1=datetime.datetime.strptime(self.task_timestamp,'%Y%m%d%H%M')
         s2=datetime.datetime.strftime(s1,'%Y-%m-%d %H:%M')
         self.db().confCompJobs.update({'confComp_uuid':self.confComp_uuid},{'$set':{'confComp_lastrun_at':s2}})
      else:
         curDatetime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
         self.db().confCompJobs.update({'confComp_uuid':self.confComp_uuid},{'$set':{'confComp_lastrun_at':str(curDatetime)}})
         
         

  def v2_playbook_on_play_start(self, play):
        pass
 
  def v2_playbook_on_task_start(self, task, is_conditional):
      pass	

  def v2_playbook_on_stats(self, stats):
     self.stats = stats
     if self.stats.dark or self.stats.failures :
	self.updateconfigDetailsInfo(self.confCompDetail_uuid,'failed')
     else:
	self.updateconfigDetailsInfo(self.confCompDetail_uuid,'ok')

  def updateconfigDetailsInfo(self,confCompDetail_uuid,status):
      self.db().confCompJobDetails.update({'confCompDetail_uuid':confCompDetail_uuid},{'$set':{'confCompDetail_status':status_code.get(status)}}) # 1 success 2 failed 

  def v2_on_any(self, *args, **kwargs):
        pass
 
  def v2_runner_on_ok(self, result):
      json_str = result._result['stdout']
      uuid1=uuid.uuid1()   
      dict1={}
      dict1['confCompJobRunResult_uuid']=str(uuid1)
      dict1['confCompJobRunResult_retJson']=json_str
      dict1['confCompJobRunResult_ip']=str(result._host)
      json_data=json.loads(str(json_str))
      dict1['confCompJobRunResult_result']=  0   # 0 means ok  1  warning 2 critical 3 failure
      dict1['confCompDetail_uuid']=self.confCompDetail_uuid
      dict1['confComp_uuid']=self.confComp_uuid
      dict1['confCompJobRunResult_datetime']=self.task_timestamp
      dict1['confCompJobRunResult_detail']='./configSummary.do?confCompJobRunResult_uuid='+str(uuid1)+'&jobType='+self.ymlName      
      self.db().confCompRunResult.insert(dict1)

  def v2_runner_on_unreachable(self, result):
      out={}
      out['confCompJobRunResult_ip']=str(result._host)
      out['confCompJobRunResult_datetime']=self.task_timestamp
      out['confCompJobRunResult_result']=3   #3  means the host unreachable
      runResult_uuid=str(uuid.uuid1())
      out['confCompJobRunResult_uuid']=runResult_uuid
      out['confCompDetail_uuid']=self.confCompDetail_uuid
      out['confComp_uuid']=self.confComp_uuid
      if result._result.has_key('msg'):
	 out['confCompRunResult_errmsg']=str(result._result['msg'])
      self.db().confCompRunResult.insert(out)

  def v2_runner_on_failed(self, result, ignore_errors=False):
     
      out={}
      out['confCompJobRunResult_ip']=str(result._host)
      out['confCompJobRunResult_datetime']=self.task_timestamp
      out['confCompJobRunResult_result']=3   #3  means the playbooks run failed
      runResult_uuid=str(uuid.uuid1())
      out['confCompJobRunResult_uuid']=runResult_uuid
      out['confCompDetail_uuid']=self.confCompDetail_uuid
      out['confComp_uuid']=self.confComp_uuid
      if result._result.has_key('msg'):
         out['confCompRunResult_errmsg']=str(result._result['msg'])
      self.db().confCompRunResult.insert(out)
		
  def v2_runner_on_skipped(self, result):
        self.res=result
