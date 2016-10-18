#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import tornado.ioloop
import tornado.web
from db import mongoOps
import pdb
#class HostsHandler(tornado.web.RequestHandler):
#class HostsHandler():
       
       # 1 group exists 0 group not exist  
def addGroup(groupName):
          res = mongoOps.db().healthCheckGroups.find_one({'group':groupName},{'_id':0})
          if res:
             return 1
          else:
             mongoOps.db().healthCheckGroups.insert({'group':groupName})
             return 0
     
       # 1 group exists delete success 0 group not exist success failed 
def deleteGroup(groupName):
          res = mongoOps.db().healthCheckGroups.find_one({'group':groupName},{'_id':0})
          if res:
             mongoOps.db().healthCheckGroups.remove({'group':groupName})
             return 1
          else:
             return 0

def findAllGroups():
          result = mongoOps.db().healthCheckGroups.find({},{'_id':0,'iplist':0})
          for res in result:
              print res
 
def findGroup(groupName):
          res = mongoOps.db().healthCheckGroups.find_one({'group':groupName},{'_id':0})
          
          res = mongoOps.db().healthCheckGroups.find_one({'group':groupName},{'_id':0})
          pass

#delete from product and os  reservedGroup is which not to delete o means no delete  1 means delete ok
def modifyIP(group,addIP):
    if group is None or addIP is None:
       return 0 
    mongoOps.db().healthCheckGroups.update({'group':group},{'$addToSet':{'iplist':addIP}},upsert=True)
    
    
    
      #0 ip exist  1 ip not exist  insert success
def addIP(groupName,ip):
          result = mongoOps.db().healthCheckGroups.find_one({'group':groupName},{'_id':0})
          if result:    # if exists this group write data , if not exist create the group
             if ip in result['iplist']:
                pass
             else:
                result['iplist'].append(ip)
                result['iplist'].sort()
                mongoOps.db().healthCheckGroups.update({'group':groupName},{'iplist':result['iplist'],'group':groupName})
          else:
             mongoOps.db().healthCheckGroups.insert({'group':groupName,'iplist':[ip]})
          osres= mongoOps.db().healthCheckGroups.find_one({'group':'os'},{'_id':0}) #must be add to os
          if osres:
             if ip in osres['iplist']:
                pass
             else: 
                osres['iplist'].append(ip)
                osres['iplist'].sort()
                mongoOps.db().healthCheckGroups.update({'group':'os'},{'iplist':osres['iplist'],'group':'os'})
          else:
             mongoOps.db().healthCheckGroups.insert({'group':'os','iplist':[ip]})
          
  


          

          
      # 0 means ip not in list delete failed 1 means ip in list delete success    
def deleteIP(groupName,ip):
          result = mongoOps.db().healthCheckGroups.find_one({'group':groupName},{'_id':0})
          if result:
             if ip in  result['iplist']:
                result['iplist'].remove(ip)
                mongoOps.db().healthCheckGroups.update({'group':groupName},{'iplist':result['iplist'],'group':groupName})
             return 1 
          else:
             return 0
             

def findIPByGroup(groupName):
          result = mongoOps.db().healthCheckGroups.find_one({'group':groupName},{'_id':0})
          if result:
             return result['iplist']
          else:
             return []
          
 
class HostsHandler(tornado.web.RequestHandler):
      def get(self):
          action = self.get_argument('action') #query delete add
          obj = self.get_argument('obj')        #  group or ip
          if action == 'query' and obj == 'ip':
             #ip = self.get_argument('ip')        # ip all or single or some
             group = self.get_argument('group')        #belongs to which group
             print group.lower()
             iplist=findIPByGroup(group.lower())
             self.write({'status':1,'msg':iplist})
             self.finish()
          elif action == 'delete' and obj == 'ip':
               pass
          elif action == 'add' and obj == 'ip':
               pass 
          elif action == 'query' and obj == 'group':
               pass
          elif action == 'delete' and obj == 'group':
               pass
          elif action == 'add' and obj == 'group':
               pass
 
