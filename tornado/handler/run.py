#!/usr/bin/python
# -*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web
import json
import demjson
import base64
import sys
import datetime
import subprocess
import os
import uuid
import time
import yaml
from db import mongoOps
import ConfigParser
from  proj  import tasks 
from proj_log import log
import pdb
'''
    the input number from param.yml
    the return number is stand for the all tasks number
'''
TIME_FORMAT='%Y-%m-%d %H:%M:%S'
#playbooksPath='/root/tornado/playbooks/'

#used for look for playbook path
def getProjPath():
#    totalPath=os.getcwdu()
#    thePath=totalPath[:totalPath.find('tornado')+8]
    thePath='/opt/tornado'
    return thePath

def get_conf(cls,key):
    cf=ConfigParser.ConfigParser()
    cf.read('/opt/tornado/conf/app.ini')
    retData=cf.get(cls,key)
    return retData
def getTotalTaskNum(yaml,machines):
    total = 0   
    circle = 0
    for sub_item in yaml:
        if sub_item['hosts'] == 'localhost' or sub_item['hosts'] == '127.0.0.1':
            total = total+1
        else:
            circle = len(sub_item['tasks'])+circle
    total = total + circle * machines
    return total
'''
   the input param is playbooks=yaml.load(file())
'''
def createPlaybookPlay(playbooks):
    plays=[]
    for sub_item in playbooks:
        dict={}
        dict['uuid']=str(uuid.uuid1())
        dict['name']=sub_item['name']
        plays.append(dict)
    return plays

def createPlayTask(yaml,json,playbook_uuid):
    for sub_item in yaml:
        sub_item['uuid']=str(uuid.uuid1())
        sub_item['playbook_uuid']=playbook_uuid
    tasklist=[]
    playlist=[]
    for sub_item in yaml:
            dict_temp={}
            dict_temp['uuid']=sub_item['uuid']
            dict_temp['name']=sub_item['name']
            playlist.append(dict_temp)
    for sub_item in yaml:
        for final_item in sub_item['tasks']:
            if sub_item['hosts'] == 'localhost' or sub_item['hosts'] == '127.0.0.1':
	       tasktemp={}
	       tasktemp['uuid']=str(uuid.uuid1())
	       tasktemp['host']='127.0.0.1'
               tasktemp['name']=final_item['name']
               tasktemp['play_uuid']=sub_item['uuid']
	       tasktemp['status']=0
               tasktemp['playbook_uuid']=playbook_uuid
	       tasktemp['created_at']=time.time()
               tasklist.append(tasktemp)
            else:
               iplist=json['ip_list']
               for ip in iplist:
                    if final_item.has_key('name'):
                       tasktemp={}
                       tasktemp['uuid']=str(uuid.uuid1())
                       tasktemp['host']=str(ip)
                       tasktemp['name']=final_item['name']
                       tasktemp['play_uuid']=sub_item['uuid']
                       tasktemp['status']=0
                       tasktemp['playbook_uuid']=playbook_uuid
                       tasktemp['created_at']=time.time()
                       tasklist.append(tasktemp)
                    if final_item.has_key('block'):
                       for subBlockItem in final_item['block']:
                           tasktemp={}
                           tasktemp['uuid']=str(uuid.uuid1())
                           tasktemp['host']=str(ip)
                           tasktemp['name']= subBlockItem['name']
                           tasktemp['play_uuid']=sub_item['uuid']
                           tasktemp['status']=0
                           tasktemp['playbook_uuid']=playbook_uuid
                           tasktemp['created_at']=time.time()
                           tasklist.append(tasktemp)
    mongoOps.InsertTasksDB(tasklist)
    log().info('run::createPlaybooktask 创建tasks成功')
    return (playlist,tasklist)

'''
   mongodb 插入playbooks 数据
'''
def createPlaybook(playbookuuid,playbookParam,playbook_yaml,playlist,tasklistNum):
    playbook_value={}
    playbook_value['uuid']=playbookuuid
    playbook_value['name']=playbookParam[1]
    playbook_value['created_at']=time.time()
    playbook_value['status']=0
    #playbook_value['total']=getTotalTaskNum(playbook_yaml,len(playbookParam[3]))
    playbook_value['total']=tasklistNum
    playbook_value['completed']=0
    playbook_value['plays']=playlist
    playbook_value['options']=str(playbookParam[4])
    #print playbookParam[3]
    playbook_value['nodes']=playbookParam[3]
    log().debug('run::createPlaybook'+str(playbook_value))
    mongoOps.InsertPlaybooksDB(playbook_value)
    log().info('run::createPlaybook success')
 

class runHandler(tornado.web.RequestHandler):
#        executor = ThreadPoolExecutor(4)
        #  根据发过来的json数据 进行解析
	def createParam(self):
            try:
               log().debug('run::createparam 收到数据'+self.request.body)
               body = json.loads(self.request.body)
            except Exception:
               retVal = {'status':'error','message':'runHandler::收到的数据不满足Json格式，请处理！'} 
               log().error('run::createParam'+'收到的数据不满足Json格式，请处理！')
               self.write(retVal)
	       self.finish()
               sys.exit(0)
            playbookuuid=body['playbook-uuid'] 
            playbookname=body['playbook-name']
            productname=body['product-name']
            nodes=body['nodes']
            paramcontent=base64.b64decode(str(body['param-content']))#playbook json参数文件 解码base64 
            #print paramcontent
            log().info('run::createparam 分解数据正常') 
            return (playbookuuid,playbookname,productname,nodes,paramcontent)

        def createFile(self,playbookname,paramcontent):
            log().info('开始创建playbook json文件')
            jsonpath=get_conf('tornado','json_path')
            currentTime=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            fileDir=jsonpath+playbookname+'/'+currentTime
            try:
               #os.mkdir(fileDir) 
               os.makedirs(fileDir) 
            except:
               retVal={'status':'error','message':'runHandler::创建存放json文件失败，请查找原因！'}
               log().error('run::createFile 创建存放json文件失败')
	       self.write(retVal)
               self.finish()
               sys.exit(0)
            JsonPath=fileDir+'/'+playbookname+'.json'  
	    try:
               fs=open(JsonPath,'w')
               fs.write(paramcontent)
               log().debug('run::createFile 写入文件的内容是'+paramcontent)
	       fs.flush()
               fs.close()
	    except Exception:
               if fs is None:
		  pass
	       else:
		  fs.close()
            return JsonPath
   
        # 客户端发送post请求后，处理的函数
        @tornado.web.asynchronous
        def post(self):
                playbookParam=self.createParam()                
                jsonPath=self.createFile(playbookParam[1],playbookParam[4])#json参数文件地址 
                playbookuuid=playbookParam[0]
        #读取配置文件
                #playbooksPath=get_conf('tornado','playbook_path')
                playbooksPath=getProjPath()+'/playbooks/deploy/'
		playbookymlpath=playbooksPath+playbookParam[1]+'.yml'
                playbook_yaml=yaml.load(file(playbookymlpath))
        # 创建playbooks 子节点plays
                plays=createPlaybookPlay(playbook_yaml)
        # create tasks
                (playlist,tasklist)=createPlayTask(playbook_yaml,demjson.decode(playbookParam[4]),playbookuuid)
		#mongoOps.InsertTasksDB(tasklist)
        #创建playbook
                tasklistNum = len(tasklist)    #获取task数量
                createPlaybook(playbookuuid,playbookParam,playbook_yaml,playlist,tasklistNum)
                #去跑playbook
                log().info('run::post 开始运行playbook')
                #tasks.deploy_run_playbook.delay(playbookParam[1],jsonPath) 
                tasks.deploy_run_playbook.apply_async(args=[playbookParam[1],jsonPath],queue='queue_deploy_run_playbook') 
                self.write({'status':'ok','message':'runhandler::初始化正确，开始运行Playbook!'})
                self.finish()
