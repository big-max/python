import os
import time
import json
import datetime
import pdb
import ConfigParser
from pymongo import MongoClient
from ansible.plugins.callback import CallbackBase
from websocket import create_connection,WebSocket
#coding=utf8

def get_conf(cls,key):
    cf=ConfigParser.ConfigParser()
    cf.read('/opt/tornado/conf/app.ini')
    retData=cf.get(cls,key)
    return retData

TIME_FORMAT='%Y-%m-%d %H:%M:%S'
statuscode = {'started':0, 'ongoing':1, 'ok':2,'skipped':4, 'unreachable':3, 'failed':3}
mongoinfo = {"host":"127.0.0.1","port":"27017","user":"","password":"","dbname":"ams"}
class CallbackModule(CallbackBase):
    def __init__(self):
    	self.completed_task = 0
    	self.playbookuuid = None
        self.task = None
        self.res=None	
        self.iplist=None 
        self.errip=None # an error occured on an ip 
        self.ws=None # websocket 
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

    # create ws      
    def ws_create_server(self):
        ip=get_conf('websocket','host')
        if self.ws == None:
           self.ws = create_connection("ws://"+ip+"/itoa/updatePlaybookStatus")

    #update the uuid's status 
    def ws_send_status(self,uuid,status): 
        last_status = str(uuid) +','+str(status)
        self.ws.send(last_status)

    def ws_receive_status(self):
        result=self.ws.recv()

    # destroy the server        
    def ws_close_server(self):
        if self.ws != None:
           self.ws.close() 
           self.ws = None
        

    def v2_playbook_on_start(self, playbook):
        now=time.time()
        self.playbook=playbook
        if self.playbook._entries[0]._variable_manager.extra_vars['playbook-uuid']:
           self.playbookuuid=self.playbook._entries[0]._variable_manager.extra_vars['playbook-uuid'] 
           iplist=self.playbook._entries[0]._variable_manager.extra_vars['ip_list'] 
           self.iplist=iplist
           hostnamelist=self.playbook._entries[0]._variable_manager.extra_vars['hostname_list'] 
           newdict=dict(zip(iplist,hostnamelist)) 
           for (key,value) in newdict.items():
               self.db().servers.update({'ip':key},{'$set':{'name':value}}) 
           uuids= self.playbookuuid.encode('gbk')
           self.db().playbooks.update({"uuid":uuids},{'$set':{"status":statuscode.get('ongoing'),"updated_at":now}})    
           self.ws_create_server()
           #time.sleep(3)  # sleep for page lazy load show
           self.ws_send_status(uuids,statuscode.get('ongoing'))
           self.ws_receive_status()
	   self.ws_close_server()

    def v2_playbook_on_play_start(self, play):
        pass
      
    def v2_playbook_on_task_start(self, task, is_conditional):
	now = time.time()
        self.task=task
        allips=self.iplist
        if self.errip:
           if self.errip in allips:
              allips.remove(self.errip)
        for okip in allips:
            self.db().tasks.update({"name":task.get_name(),"host":okip,"playbook_uuid":self.playbookuuid},{'$set':{"status":statuscode.get('ongoing'),"updated_at":now}},\
        upsert=False,multi=False)
	
    def v2_playbook_on_stats(self, stats):
        self.stats = stats
        self.ws_create_server()
        pdb.set_trace()
        if self.stats.dark or self.stats.failures :
              self.playbook_final_status(self.playbookuuid,'failed')
              self.ws_send_status(self.playbookuuid,statuscode.get('failed'))
              self.ws_receive_status()
        else:
              self.playbook_final_status(self.playbookuuid,'ok')
              self.ws_send_status(self.playbookuuid,statuscode.get('ok'))
              self.ws_receive_status()
        self.ws_close_server()
    
    def playbook_final_status(self,playbookuuid,status):
        now = time.time()
        self.db().playbooks.update({'uuid':playbookuuid},{'$set':{"status":statuscode.get(status),"updated_at":now}},upsert=False,multi=False) 
 
    def v2_on_any(self, *args, **kwargs):
        pass

    def v2_runner_on_ok(self, result):
        self.res=result
        self.UpdateLog(self.res,self.playbookuuid,'ok')
		

    def v2_runner_on_unreachable(self, result):
        self.res = result
        self.UpdateLog(self.res,self.playbookuuid, 'unreachable')

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.res=result
        
        if ignore_errors == False:
           self.UpdateLog(self.res,self.playbookuuid, 'failed',False)
        elif ignore_errors == True:
           self.UpdateLog(self.res,self.playbookuuid, 'ok',True)
        elif ignore_errors == None:
           self.UpdateLog(self.res,self.playbookuuid, 'failed',False)
        
		
    def v2_runner_on_skipped(self, result):
        self.res=result
      	self.UpdateLog(self.res,self.playbookuuid, 'skipped')
	
#  method nameMapIP  is used to translate hostname to ip
    def nameMapIP(self,namelist,iplist):
        dict={}
        namelen=len(namelist)
        iplen = len(iplist)
        if namelen == iplen:
            i=0
            while i < namelen:
                dict[namelist[i]]=iplist[i]
                i = i+1
        return dict

    def UpdateLog(self,values , playbook_uuid, status, ignore_errors=False):	
	now = time.time()
	if status == 'started':
	   currenttaskname = str(values._task.get_name())
	   self.db().tasks.update({"playbook_uuid":playbook_uuid, "name":currenttaskname},{'$set':{"status":statuscode.get(status), "updated_at":now}},upsert=False,multi=False)
	else:
	   hostsdict=dict(zip(self.task.get_variable_manager().extra_vars['hostname_list'],self.task.get_variable_manager().extra_vars['ip_list']))
           if self.errip:
              for (key,value) in hostsdict.items():  #judge if exists errip
                  if value == self.errip:
                     hostsdict.pop(key)
	   host=None
	   if values._host.get_name() =='localhost' or values._host.get_name() =='127.0.0.1':
	      host='127.0.0.1'
	   else:
	      host=str(hostsdict[values._host.get_name()]) 
	   self.db().tasks.update({"playbook_uuid":playbook_uuid, "host":host, "name":self.task.get_name()},{'$set':{"status":statuscode.get(status),"updated_at":now}})
           if status == 'failed' or status == 'unreachable':
              if ignore_errors==False:
                 self.errip=host     #  where ip has error ,save to errip
                 self.completed_task = self.completed_task + 1
                 if values._result.has_key('msg'):
                    self.db().playbooks.update({'uuid':playbook_uuid},{'$set':{'msg':values._result['msg']}})
                 if values._result.has_key('stderr'):
                    self.db().playbooks.update({'uuid':playbook_uuid},{'$set':{'stderr':values._result['stderr']}})
                 if values._result.has_key('stdout'):
                    self.db().playbooks.update({'uuid':playbook_uuid},{'$set':{'stdout':values._result['stdout']}})
              else:
                  self.completed_task = self.completed_task + 1
                  self.db().playbooks.update({"uuid":playbook_uuid},{'$set':{"completed":self.completed_task, "updated_at":now}})  
           elif status == 'ok' or status == 'skipped':
	      self.completed_task = self.completed_task + 1
	      self.db().playbooks.update({"uuid":playbook_uuid},{'$set':{"completed":self.completed_task, "updated_at":now}})
           else:
              pass
