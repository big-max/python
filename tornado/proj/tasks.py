#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import subprocess
import os
from celery import Celery
from proj.celery import app
from proj.db import mongoOps
import config
import ConfigParser
from crontab import CronTab
from healthCheck import handlerHosts 
from handler.proj_log import log
from websocket import create_connection,WebSocket
from subprocess import CalledProcessError
import pdb
import time
#used for look for playbook path
# get the config file  
def get_conf(cls,key):
    cf=ConfigParser.ConfigParser()
    cf.read('/opt/tornado/conf/app.ini')
    retData=cf.get(cls,key)
    return retData

#update the uuid's status 
def ws_send_status(ws,serverInfo=None,type1=None):
    if type1=='dict':
       ip = serverInfo['ip']
       name=serverInfo['name']
       os=serverInfo['os']
       hconf=serverInfo['hconf']
       product=serverInfo['product']
       status=serverInfo['status']
       totalOut=str(name)+':'+str(ip)+':'+str(hconf)+':'+str(os)+':'+str(product)+':'+str(status)
       ws.send("{'type':0,'msg':'"+totalOut+"'}")
    elif type1=='password':
         ws.send("{'type':1,'msg':'"+serverInfo['ip']+"'}")
    elif type1=='unreachable':
         ws.send("{'type':2,'msg':'"+serverInfo['ip']+"'}")
     
# ws recv status
def ws_receive_status(ws):
    result = ws.recv()
    log().info('get server status receive data'+ str(result))
     
# destroy the server        
def ws_close_server(ws):
    if ws != None:
       ws.close()
       ws=None

def getProjPath():
    #totalPath=os.getcwdu() 
    #thePath=totalPath[:totalPath.find('tornado')+8]
    thePath='/opt/tornado'
    return thePath
         
def getOSInfo(ip):
        try:
          ansible_param='/usr/bin/ansible '+ip + ' -i '+ ip + ', -m setup'
          retVal=subprocess.check_output([ansible_param] ,shell=True)
          log().info('receive getOSInfo::'+str(retVal))
          first=retVal.index('{')
          last=retVal.rindex('}')
          ansi_obj=json.loads(retVal[first:last+1])
          if ansi_obj['ansible_facts']['ansible_distribution']=='AIX':
             name=ansi_obj['ansible_facts']['ansible_nodename']
             hconf=str(ansi_obj['ansible_facts']['ansible_processor_cores'])+'C/'+\
             str(ansi_obj['ansible_facts']['ansible_memtotal_mb'])+'MB'
             os=ansi_obj['ansible_facts']['ansible_distribution']+' '+ansi_obj['ansible_facts']['ansible_distribution_version']\
             +'.'+ansi_obj['ansible_facts']['ansible_distribution_release'] 
             hvisor=ansi_obj['ansible_facts']['ansible_processor']
          elif ansi_obj['ansible_facts']['ansible_distribution']=='HP-UX':
             name=ansi_obj['ansible_facts']['ansible_nodename']
             hvisor=ansi_obj['ansible_facts']['ansible_virtualization_type']
             os=ansi_obj['ansible_facts']['ansible_distribution']+' '+ansi_obj['ansible_facts']['ansible_distribution_version']\
             +'.'+ansi_obj['ansible_facts']['ansible_distribution_release']
             hconf=str(ansi_obj['ansible_facts']['ansible_processor_count'])+'C/'+\
             str(ansi_obj['ansible_facts']['ansible_memtotal_mb'])+'MB'
          else:
             name=ansi_obj['ansible_facts']['ansible_nodename']
             hvisor=ansi_obj['ansible_facts']['ansible_virtualization_type']
             os=ansi_obj['ansible_facts']['ansible_distribution']+' '+ansi_obj['ansible_facts']['ansible_distribution_version']
             hconf=str(ansi_obj['ansible_facts']['ansible_processor_cores'])+'C/'+\
             str(ansi_obj['ansible_facts']['ansible_memtotal_mb'])+'MB'
          return {'name':name,'hvisor':hvisor,'os':os,'hconf':hconf}
        except Exception , e:
             print str(e)
             return 'notalive'

def getHost(status):
      out=[]
      result=None
      if status=='all':
           result=mongoOps.db().servers.find({},{'_id':0})
      else:
           result=mongoOps.db().servers.find({'status':status},{'_id':0}) 
      if result is None:
         pass 
      else:
         for server in result:
             out.append(server['ip'])
      return out  
    
def addsshcredits(ip,user,passwd):
    ping_param = 'ping '+ ip +' -c 1 -w 1'
    retVal=subprocess.call([ping_param],shell=True)
    if retVal == 1:
       return 'networkerror'
 
    ansible_os_param="/usr/bin/ansible " +ip + " -i " + ip + ", -m 'command' -a 'uname' -e 'ansible_user="+user+" ansible_ssh_pass="+passwd+"'"
    log().info('get OS Info::'+ansible_os_param)
    try:
       retVal=subprocess.check_output([ansible_os_param],shell=True)
    except CalledProcessError , mimaerror:
       log().info('get OS error::'+str(mimaerror))
       return 'passerror'
    baseDir=''
    osType = retVal.split('>>')[1].strip()
    ansible_param=''
    if user == 'root':
       if osType.lower() == 'linux': 
          baseDir='/root/'
       elif osType.lower() == 'aix':
          baseDir='/'
       ansible_param="/usr/bin/ansible " + ip + " -i " + ip + ", -m authorized_key -a 'user="+user+" key={{ lookup(\"file\",\"/root/.ssh/id_rsa.pub\") }} path='"+baseDir+".ssh/authorized_keys''  -e 'ansible_user="+user+" ansible_ssh_pass="+passwd+"'"
    else:
       baseDir='/home/'+user+'/'
       ansible_param="/usr/bin/ansible " + ip + " -i " + ip + ", -m authorized_key -a 'user="+user+" key={{ lookup(\"file\",\""+str(baseDir)+".ssh/id_rsa.pub\") }} path='"+baseDir+".ssh/authorized_keys''  -e 'ansible_user="+user+" ansible_ssh_pass="+passwd+"'"
    log().info(ansible_param)
    retVal=subprocess.call([ansible_param],shell=True)   
    if retVal == 0 :
       return 'success'
    else:
       return 'fail'

@app.task           
def updateServerInfo(servers,operation):
    ws = None 
    ip=get_conf('websocket','host')
    if ws == None:
       ws = create_connection("ws://"+ip+"/itoa/updateServerStatus")
    if isinstance(servers,dict):
       sshstatus = addsshcredits(servers['ip'],servers['userid'],servers['password'])
       if sshstatus == 'passerror':
          ws_send_status(ws,serverInfo=servers,type1='password') 
          ws_receive_status(ws)
          ws_close_server(ws)
          return
       if sshstatus == 'networkerror':
          ws_send_status(ws,serverInfo=servers,type1='unreachable')      
          ws_receive_status(ws)
          ws_close_server(ws)
          return 
       srvDict=getOSInfo(servers['ip']) 
       if srvDict == 'notalive':
          pass
       else:
          beforeList=mongoOps.db().healthCheckGroups.find({'group':{'$ne':'os'}},{'_id':0})
          server={'name':srvDict['name'],'ip':servers['ip'],'os':srvDict['os'],'hconf':srvDict['hconf'],'hvisor':srvDict['hvisor'],'product':servers['product'], 'status':'Active'}
          mongoOps.db().servers.update({'ip':server['ip']},{'$set':server},upsert=True,multi=True) 
          ws_send_status(ws,serverInfo=server,type1='dict') 
          ws_receive_status(ws)
          ws_close_server(ws)
          if 'addIP' == operation:
             for pro in servers['product'].split(','):   
                 handlerHosts.addIP(pro,servers['ip'])
          elif 'modifyIP' == operation and beforeList.count()> 0 : 
             out=[]
             for group in beforeList:
                 if servers['ip'] in group['iplist']:
                    mongoOps.db().healthCheckGroups.update({'group':group['group']},{'$pop':{'iplist':servers['ip']}})
                    out.append(group)
             for pro in servers['product'].split(','):
                 handlerHosts.modifyIP(pro,servers['ip'])  
          
    if isinstance(servers,list):
       for srv in servers:
           addsshcredits(srv['ip'],srv['userid'],srv['password'])
       for srvip in servers:
           srvDict=getOSInfo(srvip['ip'])
           if srvDict == 'notalive':
              pass
           else:
              server={'name':srvDict['name'],'ip':srvip['ip'],'os':srvDict['os'],'hconf':srvDict['hconf'],'hvisor':srvDict['hvisor'], 'status':'Active'}
              mongoOps.db().servers.update({'ip':server['ip']},{'$set':server},upsert=True,multi=True) 


@app.task
def deploy_run_playbook(ymlName,jsonPath):
    sendCommand='/usr/bin/ansible-playbook ' + getProjPath()+'/playbooks/deploy/'+ymlName+'.yml -e @'+jsonPath
    log().info(sendCommand)
    time.sleep(3) 
    retVal=subprocess.call([sendCommand],shell=True)

@app.task
def healthCheck_run_playbook(job_uuid,jobDetail_uuid,jobTarget,ymlName,task_timestamp,job_if_daily,job_scheduled_at,userName):
    sendCommand='/usr/bin/ansible-playbook ' + getProjPath()+'/playbooks/healthcheck/'\
    +ymlName+".yml -i "+jobTarget + "  -e 'task_timestamp="+task_timestamp+" jobDetail_uuid="+jobDetail_uuid+" job_uuid="+job_uuid+" ymlName="+ymlName+" job_if_daily="+job_if_daily+"'"
    log().info(sendCommand)
    if job_if_daily == '0' or job_if_daily == '1': #run immediately
       retVal = subprocess.call([sendCommand],shell=True)       
    elif job_if_daily == '2':   #run every day
       #cron = CronTab(user='root')
       cron = CronTab(user=userName)
       job=cron.new(sendCommand)
       job.setall(job_scheduled_at.split(':')[1],job_scheduled_at.split(':')[0],'*','*','*')
       cron.write(user=userName)
       log().info('healthCheck::crotab has written to crontab file.')

@app.task
def configCompare_run_playbook(job_uuid,jobDetail_uuid,jobTarget,ymlName,task_timestamp,job_if_daily,job_scheduled_at,userName):
    sendCommand='/usr/bin/ansible-playbook ' + getProjPath()+'/playbooks/configcompare/'\
    +ymlName+".yml -i "+jobTarget + "  -e 'task_timestamp="+task_timestamp+" confCompDetail_uuid="+jobDetail_uuid+" confComp_uuid="+job_uuid+" ymlName="+ymlName+" confCompDetail_if_daily="+job_if_daily+"'"
    log().info(sendCommand)
    if job_if_daily == '0': #run immediately
       retVal = subprocess.call([sendCommand],shell=True)       
    elif job_if_daily == '2':   #run every day
       cron = CronTab(user=userName)
       job=cron.new(sendCommand)
       job.setall(job_scheduled_at.split(':')[1],job_scheduled_at.split(':')[0],'*','*','*')
       cron.write(user=userName)
 
@app.task
def logCatch_run_playbook(_id,ip,product,instance,task_timestamp):
    sendCommand ='/usr/bin/ansible-playbook ' + getProjPath() +'/playbooks/logcatch/'\
    + product +"log.yml -i " + ip + ",  -e 'target="+ instance+" task_timestamp="+task_timestamp+" _id="+_id+" product="+product+" ip="+ip+"'"
    log().info(sendCommand)
    retVal = subprocess.call([sendCommand],shell=True) 
