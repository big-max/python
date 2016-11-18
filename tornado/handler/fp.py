#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web
import json
import demjson
import os
import pdb
import re
from proj_log import log
class FpHandler(tornado.web.RequestHandler):
     #得到mq版本
     def getMqVersion(self,path, ostype=None):
         log().debug('fp::getMqVersion ' + path + ' '+ ostype)
         os_dict = {'linux': '(lin|x86)', 'aix': 'aix', 'windows': 'win'}
         os_exp = os_dict.get(ostype)
         out = []
         if os_exp:
           ver_list = os.listdir(path)
           ver_list.sort()
           for ver in ver_list:
               files = os.listdir(path+'/'+ver)
               for file in files:
                   ver_search_Obj = re.search(r'ws_mq.+'+os_exp+'[^fp].*', file, re.I)
                   if ver_search_Obj:
                      ver_dict={}
                      ver_dict[ver]=ver_search_Obj.group()
                      out.append(ver_dict)
           vers = json.dumps(out)
           log().debug('fp::getMqVersion'+str(vers))
           self.write(vers)
           self.finish()
         else:
           self.write([])
           self.finish()
            

     
      #得到版本对应的补丁
     def getMqFixpack(self,path, version, ostype=None):
          log().debug('fp::getMqFixpack ' + path +' ' + str(ostype))
	  os_dict = {'linux': '(lin|x86)', 'aix': 'aix', 'windows': 'win'}
 	  os_exp = os_dict.get(ostype)
          out=[]
          final={}
  	  if os_exp:
	     files = os.listdir(path+'/'+version)
	     for elem in files:
        	 fix_search_Obj = re.search(r'(^[0-9\.]+).+'+os_exp+'.+fp0+([1-9]+).*', elem, re.I)
                 if fix_search_Obj:
	            fix_dict = {}
                    fix_dict={fix_search_Obj.group(1)+'.'+fix_search_Obj.group(3): fix_search_Obj.group()}
                    out.append(fix_dict)
                    final[version]=out
    	     fps = json.dumps(final)
             self.write(fps)
             self.finish()
          else:
             log().warning('fp::getMqFixPack  this os is not supported')
             self.write({'status':0,'message':'this os is not support.'})
             self.finish()
      
     def getwasVersion(self,path, ostype=None):
         os_dict = {'linux': '(lin|x86)', 'aix': 'aix', 'windows': 'win'}
         os_exp = os_dict.get(ostype)
         ver_dict = {}
         out=[]
         if os_exp:
            ver_list = os.listdir(path)
            ver_list.sort()
            for ver in ver_list:
	        files = os.listdir(path+'/'+ver)
	        for file in files:
	            ver_search_Obj = re.search(r'(wasnd_v'+ver+'.*)_.*zip', file, re.I)
	            if ver_search_Obj:
	               ver_dict.update({ver: ver_search_Obj.group(1)+'*zip'})
            #           ver_dict={}
            #           ver_dict[ver]=ver_search_Obj.group()
            #           out.append(ver_dict)
	    vers = json.dumps(ver_dict)
            log().debug('fp::getwasVersion'+str(vers))
            self.write(vers)
            self.finish()
         else:
            print("this os is not supported")
            self.write([])
            self.finish()
          
     def getwasFixpack(self,path, version, ostype=None):
         os_dict = {'linux': '(lin|x86)', 'aix': 'aix', 'windows': 'win'}
         os_exp = os_dict.get(ostype)
         #fix_dict = {version: {}}
         fix_dict = {}
         #final={}
         #out=[]
         if os_exp:
            files = os.listdir(path+'/'+version)
	    for elem in files:
	        fix_search_Obj = re.search(r'(^[0-9\.]+)(-ws-was-fp0+)([1-9]+)-.*zip', elem, re.I)
	        if fix_search_Obj:
         #          fix_dict={}
                   fix_dict.update({fix_search_Obj.group(1)+'.'+fix_search_Obj.group(3): fix_search_Obj.group(1)+fix_search_Obj.group(2)+fix_search_Obj.group(3)+'*zip'})
	    fps = json.dumps(fix_dict)
	    print(fps)
            self.write(fps)
            self.finish()  
         else:
            print("this os is not supported")
            self.write([])
            self.finish()
    
     def getwasIM(self,path, version, ostype=None):
         os_dict = {'linux': '(lin|x86)', 'aix': 'aix', 'windows': 'win','hpux':'hpux'}
         os_exp = os_dict.get(ostype)
         ver_dict = {}
	 #out=[]
         if os_exp:
            ver_list = os.listdir(path)
            ver_list.sort()
            for ver in ver_list:
	        files = os.listdir(path+'/'+ver)
	        for file in files:
	            ver_search_Obj = re.search(r'^agent\.installer\.'+os_exp+'.*zip', file, re.I)
	            if ver_search_Obj:
                       #ver_dict[ver]=ver_search_Obj.group()              
		       ver_dict.update({ver: ver_search_Obj.group()})
                       #out.append(ver_dict)
	    vers = json.dumps(ver_dict,indent=2)
	    print(vers)
            self.write(vers)
            self.finish()
         else:
            print("this os is not supported")
            self.write([])
            self.finish()
     
     def getihsVersion(self,path, ostype=None):
         os_dict = {'linux': '(lin|x86)', 'aix': 'aix', 'windows': 'win'}
         os_exp = os_dict.get(ostype)
         ver_dict = {}
         if os_exp:
            ver_list = os.listdir(path)
            ver_list.sort()
            for ver in ver_list:
	        files = os.listdir(path+'/'+ver)
	        for file in files:
	            ver_search_Obj = re.search(r'(was_v'+ver+'.*suppl).*zip', file, re.I)
	            if ver_search_Obj:
                       ver_dict.update({ver: ver_search_Obj.group(1)+'*zip'})
	    vers = json.dumps(ver_dict, indent=2)
            log().debug('fp::getihsVersion'+str(vers))
            self.write(vers)
            self.finish()
         else:
            log().info("this os is not supported")
            self.write([])
            self.finish()

     def getihsfixpack(self,path, version, ostype=None):
         os_dict = {'linux': '(lin|x86)', 'aix': 'aix', 'windows': 'win'}
         os_exp = os_dict.get(ostype)
         fix_dict = {}
         if os_exp:
            files = os.listdir(path+'/'+version)
	    for elem in files:
	        fix_search_Obj = re.search(r'(^[0-9\.]+)(-ws-wassupplements-fp0+)([1-9]+)-.*zip', elem, re.I)
	        if fix_search_Obj:
	           fix_dict.update({fix_search_Obj.group(1)+'.'+fix_search_Obj.group(3): fix_search_Obj.group(1)+fix_search_Obj.group(2)+fix_search_Obj.group(3)+'*zip'})
	    fps = json.dumps(fix_dict, indent=2)
            log().info('fp::ihs fix'+fps)	
            self.write(fps)
            self.finish() 
         else:
            log().info("this os is not supported")
            self.write([])
            self.finish()

     def getDb2Version(self,path, ostype=None):
         os_dict = {'linux': '(lin|x86)', 'aix': 'aix', 'windows': 'win'}
         os_exp = os_dict.get(ostype)
         ver_dict = {}
         if os_exp:
            ver_list = os.listdir(path)
            ver_list.sort()
            for ver in ver_list:
                ver_dict.update({ver: ver})
            vers = json.dumps(ver_dict, indent=2)
            log().info(vers)
            self.write(vers) 
            self.finish()
         else:
            log().info("this os is not supported")
            self.write([])
            self.finish()

     def getDb2fixpack(self,path, version, ostype=None):
         os_dict = {'linux': '(lin|x86)', 'aix': 'aix', 'windows': 'win'}
   	 os_exp = os_dict.get(ostype)
  	 fix_dict = {}
         if os_exp:
            files = os.listdir(path+'/'+version)
            for elem in files:
                fix_search_Obj = re.search(r'^v'+version+'fp([0-9]+).*'+os_exp+'.*tar.gz', elem, re.I)
        	if fix_search_Obj:
                   fix_dict.update({version+'.0.'+fix_search_Obj.group(1): fix_search_Obj.group()})
            fps = json.dumps(fix_dict, indent=2)
            log().info(fps)
            self.write(fps)
            self.finish()
         else:
    	    log().info("this os is not supported")
	    self.write([])
            self.finish()
    
     def getitmosVersion(self,path, ostype=None):
         os_dict = {'linux': '(lin|x86)', 'aix': 'aix', 'windows': 'win'}
         os_exp = os_dict.get(ostype)
         ver_dict = {}
         if os_exp:
            ver_list = os.listdir(path)
            ver_list.sort()
            for ver in ver_list:
	        files = os.listdir(path+'/'+ver)
	        for file in files:
	            ver_search_Obj = re.search(r'(ITM_V'+ver+'.*)_.*tar.gz', file, re.I)
	            if ver_search_Obj:
		       ver_dict.update({ver: ver_search_Obj.group()})
            vers = json.dumps(ver_dict, indent=2)
	    log().info(vers)
            self.write(vers)
            self.finish()
         else:
            print("this os is not supported")
            self.write([])
            self.finish()

     def getitmosFixpack(self,path, version, ostype=None):
         os_dict = {'linux': '(lin|x86)', 'aix': 'aix', 'windows': 'win'}
         os_exp = os_dict.get(ostype)
         fix_dict = {}
         if os_exp:
            files = os.listdir(path+'/'+version)
	    for elem in files:
	        fix_search_Obj = re.search(r'(^[0-9\.]+)(-TIV-ITM_TMV-Agents-FP0+)([1-9]+).tar.gz', elem, re.I)
	        if fix_search_Obj:
	           fix_dict.update({fix_search_Obj.group(1)+'.'+fix_search_Obj.group(3): fix_search_Obj.group(1)+fix_search_Obj.group(2)+fix_search_Obj.group(3)+'.tar.gz'})
	    fps = json.dumps(fix_dict, indent=2)
            log().info(fps)
            self.write(fps)
            self.finish()
         else:
            log().info("this os is not supported")
            self.write([])
            self.finish()

     @tornado.web.asynchronous
     def post(self):
         log().debug('fp::post 收到数据'+self.request.body) 
         body = json.loads(self.request.body)
         pName=body['pName']
         platform=body['platform']
         if pName =='db2':
            db2Path=body['db2Path']
            if 'version'==body['type']:
               self.getDb2Version(db2Path,platform)
            elif 'fix' == body['type']:
                version=body['version']
                self.getDb2fixpack(db2Path,version,platform)
         elif pName =='itmos':
              itmosPath=body['itmosPath']
              if 'version' == body['type']:
                 self.getitmosVersion(itmosPath,platform)
              elif 'fix'==body['type']:
                 version=body['version']
                 self.getitmosFixpack(itmosPath,version,platform)
         elif pName =='ihs':
              ihsPath=body['ihsPath']
              if 'version' == body['type']:
                 self.getihsVersion(ihsPath,platform)
              elif 'fix'==body['type']:
                 version=body['version']
                 self.getihsfixpack(ihsPath,version,platform)
              elif 'im' == body['type']:
                 version=body['version']
                 self.getwasIM(ihsPath,version,platform)
         elif pName =='was':
              wasPath=body['wasPath']
              if 'version' == body['type']:
                 self.getwasVersion(wasPath,platform)
              elif 'fix'==body['type']:
                 version=body['version']
                 self.getwasFixpack(wasPath,version,platform)
              elif 'im' == body['type']:
                 version=body['version']
                 self.getwasIM(wasPath,version,platform) 
            
         elif pName == 'mq':
              mqPath=body['mqPath']
              if 'fix'==body['type']:
                  version=body['version']
                  self.getMqFixpack(mqPath,version,platform)
              elif 'version' == body['type']:
                   self.getMqVersion(mqPath,platform)       
         else:
            self.write({'status':0,'message':'you input a error message'})
            log().info('fp::post 你输入了错误的信息')
            self.finish() 
