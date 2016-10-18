#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web
import json
from db import mongoOps
import pdb
import re
import time
import uuid
import subprocess
#from concurrent.futures import ThreadPoolExecutor
import pymongo
import functools
from proj import tasks
from proj_log import log
#创建服务器类
class srvHandler(tornado.web.RequestHandler):

    #创建一台服务器，加密秘钥 1 success      
      @tornado.web.asynchronous
      @tornado.gen.coroutine
      def createServer(self,target):
          servers=[]
          servers.append(target['ip'])
          try:
             result=mongoOps.db().servers.insert(target)
             log().debug('servers::createServer'+str(result))
             if result is None:
                self.write({"status":0,"message":"创建服务器失败！"})
                log().info('servers::createServer'+'创建服务器失败')
                self.finish()
             else:
                #tasks.updateServerInfo.delay(servers)
                #tasks.updateServerInfo.delay(servers)
                del target['_id']  #删除_id 无法取出_id 值
                #tasks.updateServerInfo.delay(target)
                # addIP represitent operation is add a server then add ip to group
                tasks.updateServerInfo.apply_async(args=[target,'addIP'],queue='default')
                self.write({"status":1,"message":"创建服务器成功!"})
                log().info('servers::createServer'+"创建服务器成功!")
                self.finish()
                #tasks.updateServerInfo.apply_async(servers)
          except Exception ,e :
                print e 
                self.write({"status":0,"message":"调用mongoDB出错，出错为"+str(e)})
                log().error("servers::createServer调用mongoDB出错，出错为"+str(e))
                self.finish()

      # 通过Excel 导入 多台服务器[{},{},{}]      1成功 0 失败
      def importExcel(self,lists):
          out=lists #定义已经存在的IP，无法通过excel导入
          for server in lists:
              try:
                 result=mongoOps.db().servers.insert(server)
              except pymongo.errors.DuplicateKeyError,e1:
                 out.remove(server)
                 continue
              except Exception ,e :
                  self.write({'status':0,'message':'出错，出错原因为:'+str(e)})
                  self.finish()
          #tasks.updateServerInfo.delay(all_ip_list)
          tasks.updateServerInfo.delay(out)
          self.write({'status':1,'message':'成功导入服务器!'})
          self.finish()
             
       
      def IPCheck(self,ip):
          try:
             result=mongoOps.db().servers.find({"ip":ip})
	     length=result.count()
             if length<=0:
                self.write({"status":0,"message":"不存在!"})
                self.finish()
             else:
                self.write({"status":1,"message":"已经存在!"})
	        self.finish()
          except Exception ,e :
             self.write({"status":0,"message":"调用mongodb IPCheck出错,错误描述为:"+str(e)})
             self.finish()
      
      #根据playbook setup 模块更新servers表 
      def updateServers(self,servers):
          now = time.time()
          for server in servers:
              ip=server['IP']          
              mongoOps.db().servers.update({'IP':ip},{'$set':{'Name':server['Name'],'OS':server['OS'],'HConf':server['HConf']}})
          self.write({'status':1,'message':'yes'})
          self.finish()
       

      #修改主机信息，只能修改ip userid password 
      def modifyServer(self,server):
          result=mongoOps.db().servers.update({'uuid':server['uuid']},{'$set':{'userid':server['userid'],\
          'password':server['password'],'ip':server['ip'],'product':server['product']}})
          if result['n']==1: 
              #tasks.updateServerInfo.delay(server)
              tasks.updateServerInfo.apply_async(args=[server,'modifyIP'],queue='default')
              self.write({'status':1,'message':'修改成功'})
          else: 
              self.write({'status':0,'message':'修改失败'})
          self.finish()

      def deleteServers(self,servers):
          out=[]    #定义删除失败的主机
          for uuid in servers:
              result=mongoOps.db().servers.remove({'uuid':uuid['uuid']})          
              if result['ok']==0 or  result['n']==0:
                 out.append(uuid['uuid'])
          if len(out) != 0:
              self.write({'status':1,'message':'存在uuid 为:'+str(out)+'删除失败'})
          else:
              for ip in servers:
                  mongoOps.db().healthCheckGroups.update({},{'$pop':{'iplist':ip['ip']}},upsert=False,multi=True)
              self.write({'status':1,'message':'删除成功'})
          self.finish()

      @tornado.web.asynchronous
      @tornado.gen.coroutine
      def post(self):
          try:
             log().debug('servers::'+self.request.body)
             body = json.loads(self.request.body)
             operType=body['type']
             if operType == 'createServer':
                server=body['server']
                self.createServer(server)             
             elif operType =='importExcel':
                servers=body['servers']
                self.importExcel(servers)
             elif operType =='IPCheck':
                ip=body['IP']
                self.IPCheck(ip)
             elif operType == 'deleteServer':
                servers=body['servers']
                self.deleteServers(servers)
             elif operType == 'modifyServer':
                server=body['server']
                self.modifyServer(server)
             else:
                self.write({"status":0,"message":"你提供了错误的代码，无法返回数据"})
                log().error("servers::你提供了错误的代码，无法返回数据")
                self.finish()
          except Exception ,e :
             log().error('servers::'+str(e))
             self.write({"status":0,"message":str(e)})
             self.finish()

