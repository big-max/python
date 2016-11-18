#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web
import json
import os
import pdb
import re
from handler import proj_log
from db import mongoOps
import pymongo
import time
import uuid
import base64
import datetime

class LogDownloadHandler(tornado.web.RequestHandler):
      @tornado.web.asynchronous
      def post(self):
          body=json.loads(self.request.body)
          _id=body['_id']
          res=mongoOps.db().logCatch.find_one({'_id':_id})
          location=res['loc']
          buf_size=1000
          self.set_header('Content-Type','application/ostet-stream') #很重要
          with open(location,'rb') as f:
               while True:
                     data=f.read(buf_size)
                     if not data:
                        break
                     self.write(data)
          self.finish()
