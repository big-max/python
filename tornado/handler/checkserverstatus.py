#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web
import json
import demjson
import subprocess
import base64
import os
import pdb
import re
from proj_log import log
from db import mongoOps
from proj import tasks
import pdb
def addsshcredits(ip,user,passwd):
    ansible_os_param="/usr/bin/ansible " +ip + " -i " + ip + ", -m 'command' -a 'uname' -e 'ansible_user="+user+" ansible_ssh_pass="+passwd+"'"   
    log().info('get OS Info::'+ansible_os_param)
    retVal=subprocess.check_output([ansible_os_param],shell=True)
    baseDir=''
    osType = retVal.split('>>')[1].strip()
    ansible_param=''
    if user == 'root':
       if osType.lower() == 'linux':
          baseDir='/root/'
       elif osType.lower() == 'aix':
          baseDir='/'
       elif osType.lower() == 'hp-ux':
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
 




def getOSInfo(ip):
        try:
          ansible_param='/usr/bin/ansible '+ip + ' -i '+ ip + ', -m setup'
          retVal=subprocess.check_output([ansible_param] ,shell=True)
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

# this function returns a dict about ip:1 or ip:0 ip:2 status
def getIPStatus(srvList):
    retDict={}
    for srv in srvList:
        param = 'ping '+ srv +' -c 1 -w 1'
        try:
           p = subprocess.Popen([param],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
           out=p.stdout.read()
           regex=re.compile('100% packet loss')
           if len(regex.findall(out)) == 0:   # the host is unreachable
              retDict[srv]=1                 # 1 means ok     
           else:
              retDict[srv]=0                 # 0 means error  
        except:
           log().info('the network work error')
           retDict[srv]=2                 # 2 means network error 
    return retDict
              
def judgeServerStatus(srvList):
    statusDict=getIPStatus(srvList)
    outDict={}
    for srv in statusDict:
       try:
          if statusDict[srv] == 1:     #  reachable 
             result = mongoOps.db().servers.find_one({'ip':srv},{'_id':0})
             ret=addsshcredits(srv,result['userid'],result['password'])            
             log().info('addssh::'+ret)
             if ret =='success':
                osInfo = getOSInfo(srv)  # get update infomation
                mongoOps.db().servers.update({'ip':srv},{'$set':{'name':osInfo['name'],'hvisor':osInfo['hvisor'],'os':osInfo['os'],'hconf':osInfo['hconf'],'status':'Active'}})
                outDict[srv]=1
             else:
                outDict[srv]=2    # 2 means ping is ok ,but ssh exist error
          else:   # the return valu is 0 or 2 means error
              mongoOps.db().servers.update({'ip':srv},{'$set':{'status':'Error'}})
              outDict[srv]=0
       except Exception , e:
              print e 
              outDict[srv]=3   # 3 means non know error      
    return outDict
     
#加上IP地址有效性判断
class checkServerStatusHandler(tornado.web.RequestHandler):
      @tornado.web.asynchronous
      def post(self):
          body = json.loads(self.request.body)
          selectedServers=body['servers']
          srvlist=selectedServers.split(',')
          retData = judgeServerStatus(srvlist)
          self.write({'status':1,'msg':retData})
          self.finish()


# 检查playbook 跑的状态
class checkPlaybookStatusHandler(tornado.web.RequestHandler):
      @tornado.web.asynchronous
      def post(self):
          playbookstatusbody=base64.b64decode(self.request.body)
          body = json.loads(playbookstatusbody)
          out=[]
          vers=''     
          for uuid in body:
              inner_data={}
              result=mongoOps.db().playbooks.find_one({'uuid':uuid['playbookuuid']},{'_id':0})
              status = result['status']
              inner_data[uuid['playbookuuid']]=status
              out.append(inner_data)
          vers = json.dumps(out)             
   
          if vers != '': 
             self.write({'status':1,'msg':vers})
          else:
             self.write({'status':0,'msg':'failed'})
          self.finish()

      
