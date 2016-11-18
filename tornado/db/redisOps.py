#!/usr/bin/env python
# -*- coding:utf-8 -*-
import redis

class Database:  
    def __init__(self):  
        self.host = 'localhost'  
        self.port = 6379  

    def write(self,playbookuuid,playbookstatus):  
        try:  
            r = redis.StrictRedis(host=self.host,port=self.port)  
            r.set(key,val)  
        except Exception, exception:  
            print exception  

    def read(self,playbookuuid,playbookstatus):  
        try:  
            r = redis.StrictRedis(host=self.host,port=self.port)  
            value = r.get(key)  
            print value  
            return value  
        except Exception, exception:  
            print exception  

if __name__ == '__main__':  
    db = Database()  
    db.write('sfasdfds','1')  
    #db.read('meituan','beijing',2013,9,1)  

