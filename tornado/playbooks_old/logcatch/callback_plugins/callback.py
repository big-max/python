import os
import time
import json
import datetime
import pdb
from pymongo import MongoClient
from ansible.plugins.callback import CallbackBase
#coding=utf8
TIME_FORMAT='%Y-%m-%d %H:%M:%S'
pro_detail_path='/scripts/logcatch/'
statuscode = {'started':0, 'ongoing':1, 'ok':2,'skipped':4, 'unreachable':3, 'failed':3}
mongoinfo = {"host":"127.0.0.1","port":"27017","user":"","password":"","dbname":"ams"}
class CallbackModule(CallbackBase):
    def __init__(self):
        self._id=None
        self.product=None
        self.task_timestamp=None
        self.ip=None
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
        self._id=playbook._entries[0]._variable_manager.extra_vars['_id']
        self.product=playbook._entries[0]._variable_manager.extra_vars['product']
        self.task_timestamp=playbook._entries[0]._variable_manager.extra_vars['task_timestamp']
        self.ip=playbook._entries[0]._variable_manager.extra_vars['ip']

    def v2_playbook_on_play_start(self, play):
        pass
      
    def v2_playbook_on_task_start(self, task, is_conditional):
        pass
	
    def v2_playbook_on_stats(self, stats):
        pass
 
    def v2_on_any(self, *args, **kwargs):
        pass

    def v2_runner_on_ok(self, result):
        self.res=result
        if str(result._task) == 'TASK: retrieve '+self.product+' generic data from client':
           loc=pro_detail_path+self.product+"/"+self.task_timestamp + "/runras-"+str(result._host)+".zip"
           url='logCatch_download_log.do?_id='+self._id+'&product='+self.product+'&ip='+self.ip
           self.db().logCatch.update({'_id':self._id},{'$set':{'operation':'download','loc':loc,'url':url}}) 

    def v2_runner_on_unreachable(self, result):
        self.res = result

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.res = result
		
    def v2_runner_on_skipped(self, result):
        self.res=result
