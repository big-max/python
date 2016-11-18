#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.web
import tornado.ioloop
import pdb
import re
import json
from db import mongoOps
from concurrent.futures import ThreadPoolExecutor
import functools
import pymongo
class dictHandler(tornado.web.RequestHandler):
       #根据tasks中文换英文
      def changeEngToChinese(self,type1):
          result = mongoOps.db().dict.find({'type':type1},{'_id':0})
          out = []
          for i in result:
              out.append(i)
          self.write(json.dumps(out))
          self.finish()

      @tornado.web.asynchronous
      def get(self):
          type=self.get_argument("type")
          self.changeEngToChinese(type)          
          

class serversHandler(tornado.web.RequestHandler):
       #通过os筛选主机 aix \ windows\linux      
      def getOSServers(self,os):
          arr=['aix','windows','linux']
          if os.lower() not in arr:
              self.write({'status':'info','message':'您查找的内容不存在！'})
              self.finish()
              return 
          if os.lower() == 'aix':
             result=mongoOps.db().servers.find({"OS":{'$regex':os}},{'_id':0})
             if result is None:
                self.write({"status":0,"message":'没有查到适合的aix主机！'})
                self.finish()
             else:
                out=[]
                for server in result:
                    out.append(server)
                self.write(json.dumps(out))
                self.finish()
          elif os.lower() == 'windows':
               result=mongoOps.db().servers.find({"OS":{'$regex':os}},{'_id':0})
               if result is None:
                  self.write({"status":0,"message":'没有查到适合的windows主机！'})
                  self.finish()
               else:
                  out=[]
                  for server in result:
                      out.append(server)
                  self.write(json.dumps(out))
                  self.finish()
          else:
               result=mongoOps.db().servers.find({"OS":{'$ne':{'$regex':'aix','$regex':'windows'}}},{'_id':0})
               if result is None:
                  self.write({"status":0,"message":'没有查到适合的linux主机！'})
                  self.finish()
               else:
                  out=[]
                  for server in result:
                      out.append(server)
                  self.write(json.dumps(out))
                  self.finish()

      def getOneServer(self,uuid):
	  result=mongoOps.db().servers.find_one({"uuid":uuid},{'_id':0})
	  if result is None:
             self.write({"status":"info","message":"您找的"+str(uuid)+"不存在!"})
	     self.finish()
          else:
             self.write(json.dumps(result))
             self.finish()
       
      def getOneServerByIp(self,ipaddr):
          ips=ipaddr.encode('gbk')
	  result=mongoOps.db().servers.find_one({"IP":ips},{'_id':0})
	  if result is None:
             self.write({"status":"info","message":"您找的"+str(ipaddr)+"不存在!"})
	     self.finish()
          else:
             self.write(json.dumps(result))
             self.finish()
        
      @tornado.web.asynchronous
      @tornado.gen.coroutine
      def getAllServers(self):
	  result=mongoOps.db().servers.find({},{'_id':0})
          out=[]
          for server in result:
              out.append(server)
          self.write(json.dumps(out))
          self.finish()

      #当参数为odata/servers , odata/servers? ,odata/servers?uuid= 这三种情况是查询所有的servers
      #当参数为odata/server?uuid=字符串 则返回一条内容
      @tornado.web.asynchronous
      @tornado.gen.coroutine
      def get(self):
          #pdb.set_trace()
          uuid=self.get_argument("uuid",'withoutuuid') 
          if uuid is None or uuid.strip() =='': 
             self.getAllServers()
          elif uuid == 'withoutuuid':
             ip = self.get_argument('ip','withoutos')
             if ip is None or ip.strip() =='': 
                self.getAllServers()
             elif ip == 'withoutos':
                os = self.get_argument('os','default')
                if os is None or os.strip() =='':
                   self.getAllServers()
                elif os =='default':
                   self.getAllServers()
                else:
                   self.getOSServers(os)
             else:
                self.getOneServerByIp(ip)
          else:
             self.getOneServer(uuid) 

class tasksHandler(tornado.web.RequestHandler):
      def getOneTask(self,uuid):
          result=mongoOps.db().tasks.find_one({"uuid":uuid},{'_id':0})
          if result is None:
             self.write({"status":"info","message":"您找的"+str(uuid)+"不存在!"})
             self.finish()
          else:
             self.write(str(result).decode('utf8'))
             self.finish()

      def getAPlayBookTasks(self,uuid):
          result=mongoOps.db().tasks.find({"playbook_uuid":uuid},{'_id':0}).sort('created_at',pymongo.ASCENDING) #按照时间升序
          if result is None:
             self.write({"status":"info","message":"您找的playbook"+str(uuid)+"不存在!"})
             self.finish()
          else:
             out=[]
             for task in result:
                 out.append(task)
             self.write(json.dumps(out))
             self.finish()     

      def getAllTasks(self):
          result=mongoOps.db().tasks.find({},{'_id':0})
          out=[]
          for task  in result:
              out.append(task)
          self.write(json.dumps(out))
          self.finish()

      #当参数为odata/tasks , odata/tasks? ,odata/tasks?uuid= 这三种情况是查询所有的tasks
      #当参数为odata/tasks?uuid=字符串 则返回一条内容
      @tornado.web.asynchronous
      def get(self):
          uuid=self.get_argument("uuid",'withoutuuid')
          if uuid is None or uuid.strip() =='': 
             self.getAllTasks()
          elif uuid=='withoutuuid':
               uuid=self.get_argument('playbook_uuid','default')
               self.getAPlayBookTasks(uuid)
          else:
             self.getOneTask(uuid)

class playbooksHandler(tornado.web.RequestHandler):
      def getOnePlayBook(self,uuid):
	  result=mongoOps.db().playbooks.find_one({"uuid":uuid},{'_id':0})
	  if result is None:
             self.write({"status":"info","message":"您找的"+str(uuid)+"不存在!"})
	     self.finish()
          else:
             self.write(json.dumps(result))
             self.finish()
       
      def getAllPlayBooks(self):
	  result=mongoOps.db().playbooks.find({},{'_id':0}).sort('created_at',pymongo.DESCENDING)  #降序
          out=[]
          for playbook in result:
              out.append(playbook)
          self.write(json.dumps(out))
          self.finish()

      #当参数为odata/playbooks , odata/playbooks? ,odata/playbooks?uuid= 这三种情况是查询所有的servers
      #当参数为odata/playbooks?uuid=字符串 则返回一条内容
      @tornado.web.asynchronous
      def get(self):
          uuid=self.get_argument("uuid",'withoutuuid') 
          if uuid is None or uuid.strip() =='' or uuid=='withoutuuid':
             self.getAllPlayBooks()
          else:
             self.getOnePlayBook(uuid)
