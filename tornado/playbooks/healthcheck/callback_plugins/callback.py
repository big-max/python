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
pro_detail_path='/scripts/healthcheck/'

class CallbackModule(CallbackBase):
    def __init__(self):
        self.job_uuid=None
        self.jobDetail_uuid=None
        self.ymlName=None
        self.task_timestamp=None
        self.job_if_daily=None
#        self.healthJobsRunResult_uuid=None
        self.IPMapRunResult_uuid={}    # ip map runresult_uuid
 #       self.jobUUID=None
        self.jobErrUUID={}
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
        self.jobDetail_uuid=playbook._entries[0]._variable_manager.extra_vars['jobDetail_uuid']
        self.job_uuid=playbook._entries[0]._variable_manager.extra_vars['job_uuid']
        self.ymlName=playbook._entries[0]._variable_manager.extra_vars['ymlName']
        self.task_timestamp=playbook._entries[0]._variable_manager.extra_vars['task_timestamp']
        self.job_if_daily=playbook._entries[0]._variable_manager.extra_vars['job_if_daily']
        self.db().healthJobDetails.update({'job_uuid':self.job_uuid},{'$set':{'jobDetail_status':3}})
        
    def v2_playbook_on_play_start(self, play):
        if self.job_if_daily == '2' :    #  run every day is start 
           curDatetime=datetime.datetime.now().strftime('%Y%m%d') # whenrunit,update jobdetail
           self.task_timestamp = str(curDatetime) + str(self.task_timestamp)
           s1=datetime.datetime.strptime(self.task_timestamp,'%Y%m%d%H%M') 
           s2=datetime.datetime.strftime(s1,'%Y-%m-%d %H:%M')
           self.db().healthJobs.update({'job_uuid':self.job_uuid},{'$set':{'job_lastrun_at':s2}})
        else:
           curDatetime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
           self.db().healthJobs.update({'job_uuid':self.job_uuid},{'$set':{'job_lastrun_at':str(curDatetime)}})
      
    def v2_playbook_on_task_start(self, task, is_conditional):
        pass	

    def v2_playbook_on_stats(self, stats):
        self.stats = stats
        if self.stats.dark or self.stats.failures :
           self.updateHealthJobDetailsInfo(self.jobDetail_uuid,'failed')
        else:
           self.updateHealthJobDetailsInfo(self.jobDetail_uuid,'ok')

    def updateHealthJobDetailsInfo(self,jobDetail_uuid,status):
        self.db().healthJobDetails.update({'jobDetail_uuid':jobDetail_uuid},{'$set':{'jobDetail_status':status_code.get(status)}}) # 1 success 2 failed

           

    def v2_on_any(self, *args, **kwargs):
        pass

    def updateHealthJobRunResult(self,result):
        if str(result._task) == 'TASK: retrieve os summary health check data':
           json_str = result._result['stdout'] 
           uuid1=uuid.uuid1()  #create uuid os first    
           dict1={}
           dict1['healthJobsRunResult_uuid']=str(uuid1)
           dict1['healthJobsRunResult_retJson_os']=json_str
           dict1['healthJobsRunResult_ip']=str(result._host)
           json_data=json.loads(str(json_str))
           dict1['healthJobsRunResult_result']=json_data['status']
           dict1['jobDetail_uuid']=self.jobDetail_uuid
           dict1['job_uuid']=self.job_uuid
           dict1['healthJobsRunResult_datetime']=self.task_timestamp
           os_summ_loc=pro_detail_path+"oshc/"+self.task_timestamp + "/oshc-"+str(result._host) 
           dict1['healthJobsRunResult_os_summary_loc']=os_summ_loc
           dict1['healthJobsRunResult_detail']='./healthCheck_summary.do?healthJobsRunResult_uuid='+str(str(uuid1))+'&jobType='+self.ymlName
           self.db().healthJobRunResult.insert(dict1)
           #self.healthJobsRunResult_uuid=str(uuid1)
           self.IPMapRunResult_uuid[str(result._host)]=str(uuid1)
        if str(result._task) == 'TASK: retrieve mq summary health check data' or str(result._task) == 'TASK: retrieve db2 summary health check data' or str(result._task) == 'TASK: retrieve was summary health check data':
           json_str=result._result['stdout']
           out={}
           out['healthJobsRunResult_ip']=str(result._host)
           json_data=json.loads(str(json_str))
           out['healthJobsRunResult_result']=json_data['overall']
           #_uuid=self.healthJobsRunResult_uuid
           _uuid=self.IPMapRunResult_uuid[str(result._host)]
           healthJobsRunResult_uuid=str(_uuid)
           out['healthJobsRunResult_detail']='./healthCheck_summary.do?healthJobsRunResult_uuid='+str(healthJobsRunResult_uuid)+'&jobType='+self.ymlName
           out['jobDetail_uuid']=self.jobDetail_uuid
           out['job_uuid']=self.job_uuid
           summ_loc=pro_detail_path+self.ymlName+"/"+self.task_timestamp + "/"+self.ymlName+"-"+str(result._host)          
           os_summ_loc=pro_detail_path+"oshc/"+self.task_timestamp + "/oshc-"+str(result._host)          
           out['healthJobsRunResult_summary_loc']=summ_loc
           out['healthJobsRunResult_os_summary_loc']=os_summ_loc
           out['healthJobsRunResult_retJson']=json_str
           out['healthJobsRunResult_datetime']=self.task_timestamp
           self.db().healthJobRunResult.update({'healthJobsRunResult_uuid':healthJobsRunResult_uuid},{'$set':{'healthJobsRunResult_ip':out['healthJobsRunResult_ip'],'healthJobsRunResult_result':out['healthJobsRunResult_result'],'healthJobsRunResult_detail':out['healthJobsRunResult_detail'],'jobDetail_uuid':out['jobDetail_uuid'],'job_uuid':out['job_uuid'],'healthJobsRunResult_summary_loc':out['healthJobsRunResult_summary_loc'],'healthJobsRunResult_os_summary_loc':out['healthJobsRunResult_os_summary_loc'],'healthJobsRunResult_retJson':out['healthJobsRunResult_retJson'],'healthJobsRunResult_datetime':out['healthJobsRunResult_datetime']}})

 
    def v2_runner_on_ok(self, result):
        self.updateHealthJobRunResult(result)   

    def v2_runner_on_unreachable(self, result):
           out={}
           out['healthJobsRunResult_ip']=str(result._host)
           out['healthJobsRunResult_datetime']=self.task_timestamp
           out['healthJobsRunResult_result']=3   #3  means the host unreachable
           runResult_uuid=str(uuid.uuid1())
           out['healthJobsRunResult_uuid']=runResult_uuid
           out['jobDetail_uuid']=self.jobDetail_uuid
           out['job_uuid']=self.job_uuid
           
           self.db().healthJobRunResult.insert(out)
           self.db().healthJobRunResult.update({'healthJobsRunResult_uuid':str(runResult_uuid)},{'$set':{'healthJobsRunResult_errmsg':str(result._result['msg'])}})    #run failed need status 2 need errmsg 

    def v2_runner_on_failed(self, result, ignore_errors=False):
      if ignore_errors == False:
        err_host = str(result._host)
        uuid1=uuid.uuid1()
        errmsg=''
        try:
           errmsg = errmsg+result._result['msg'] +" "
        except Exception :
           errmsg=''
        try:
           errmsg = errmsg+result._result['stderr'] + " "
        except Exception :
           pass
        try:
           errmsg = errmsg+result._result['stdout'] 
        except Exception :
           pass

        try:
           errUUID=self.IPMapRunResult_uuid[err_host]
           if errUUID:        #find the uuid which ip mapped to  
              self.db().healthJobRunResult.update({'healthJobsRunResult_uuid':errUUID},{'$set':{'healthJobsRunResult_result':3,'healthJobsRunResult_errmsg':errmsg}})    #run failed need status 2 need errmsg 
           else:   #  get osinfo failure so need to create a runresult_uuid
              out={}
              out['healthJobsRunResult_ip']=str(result._host)
              out['healthJobsRunResult_datetime']=self.task_timestamp
              out['healthJobsRunResult_result']=3   #3  means the host unreachable
              runResult_uuid=str(uuid1)
              out['healthJobsRunResult_uuid']=runResult_uuid
              out['jobDetail_uuid']=self.jobDetail_uuid
              out['job_uuid']=self.job_uuid
              out['healthJobsRunResult_errmsg']=errmsg
              self.db().healthJobRunResult.update({'healthJobsRunResult_uuid':runResult_uuid},{'$set':out},upsert=True)    #run failed need status 2 need errmsg 
        except KeyError as e:
                 #out['healthJobsRunResult_uuid']=uuid1
                 out={}
                 out['healthJobsRunResult_ip']=str(result._host)
                 out['healthJobsRunResult_datetime']=self.task_timestamp
                 out['healthJobsRunResult_result']=3   #3  means the host unreachable
                 runResult_uuid=str(uuid1)
                 #out['healthJobsRunResult_uuid']=runResult_uuid
                 out['jobDetail_uuid']=self.jobDetail_uuid
                 out['job_uuid']=self.job_uuid
                 out['healthJobsRunResult_errmsg']=errmsg
                 #if self.jobErrUUID[str(result._host)] is not None:
                 if self.jobErrUUID.has_key(str(result._host)):
                    out['healthJobsRunResult_uuid']=self.jobErrUUID[str(result._host)]
                    self.db().healthJobRunResult.update({'healthJobsRunResult_uuid':self.jobErrUUID[str(result._host)]},{'$set':out},upsert=True)    #run failed need status 2 need errmsg 
            #        self.jobErrUUID={}
                 else:
                    out['healthJobsRunResult_uuid']=str(uuid1)
                    self.db().healthJobRunResult.update({'healthJobsRunResult_uuid':str(uuid1)},{'$set':out},upsert=True)    #run failed need status 2 need errmsg 
                    self.jobErrUUID[str(result._host)]=str(uuid1)
                  
		
    def v2_runner_on_skipped(self, result):
        self.res=result
	

