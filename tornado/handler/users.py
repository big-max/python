#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web
import json
from db import mongoOps
import pdb
from  proj_log import log
class usersHandler(tornado.web.RequestHandler):

      # 检查账号是否存在
      def checkUser(self,userName):
          if userName == None:
             raise ValueError('参数不能为空') 
          result=mongoOps.db().login.find_one({'name':userName})
          if result:
             self.write({'status':1,'msg':1})
          else:
             self.write({'status':1,'msg':0})
          self.finish() 

      # 添加用户
      def addUser(self,name,password,role,email,product):
          user={'name':'default','password':'default','role':0,'email':'itoa@xxx.com','product':[]}
          user['name']=name
          user['password']=password
          user['role']=role
          user['email']=email
          user['product']=product
          result=mongoOps.db().login.insert(user)
          if result:
             self.write({'status':1,'msg':'添加用户成功'})
          else:
             self.write({'status':0,'msg':'添加用户失败'})
          self.finish()
          

      # 删除用户
      def delUser(self,names):
          try:
            for name_one in names:
                result=mongoOps.db().login.remove({'name':name_one})
            self.write({'status':1,'msg':'删除成功'})
          except Exception , e:
            self.write({'status':0,'msg':'删除失败,失败原因为:'+str(e)})
          self.finish()
         
      def login(self,name,passwd,role):
	  try:
             #log().debug('login::'+name+ ' '+passwd+ ' ' +str(role))
             result=mongoOps.db().login.find_one({'name':name},{'_id':0})
             if result is None:
                self.write({'status':0,'message':'账号不存在,或账号权限非法！'})
                log().info('login::账号不存在,或账号权限非法！')
                self.finish()
             else:
                if passwd == result['password']:
                   del result['password']
                   del result['email']
                   product=result['product']
                   out=','.join(product)     
                   result['product']=out
                   self.write({'status':1,'message':json.dumps(result)})
                   log().info('login::'+name+' login success')
                   self.finish()       
                else:
                   self.write({'status':0,'message':'密码错误!'})
                   log().info('login::密码错误！')
                   self.finish() 
          except Exception , err:
                self.write({'status':0,'message':'登录异常，异常为:'+str(err)})   
                log().error('login::登录异常，异常为'+str(err))
		self.finish()

      @tornado.web.asynchronous
      def get(self):
          out=[]
          result= mongoOps.db().login.find({},{'_id':0})
          for res in result:
              out.append(res)
          self.write(json.dumps(out))
          self.finish()

          
      @tornado.web.asynchronous
      def post(self):
          try:
             body = json.loads(self.request.body)
             operType=body['type']
             if operType == 'login':
                log().info('login::user start login')
                name=body['name']
	        password=body['password']
	        role=body['role']
                self.login(name,password,role)
             elif operType == 'checkUser':
                name=body['name']
                self.checkUser(name)
             elif operType == 'addUser':
                name=body['name']
	        password=body['password']
	        role=body['role']
                email=body['email'] 
                product=body['product']
                self.addUser(name,password,role,email,product)
             elif operType == 'delUser':
	        name=body['name']
                self.delUser(name)
             else:
                self.write({"status":0,"message":"调用/api/v1/users/接口异常,请检查参数类型!"})
                log().error('调用/api/v1/users接口异常，请检查参数')
                self.finish()
          except Exception ,e :
                self.write({"status":0,"message":"JSon解析数据异常,出错为"+str(e)})
                log().error({"status":0,"message":"JSon解析数据异常,出错为"+str(e)})
                self.finish()
                
