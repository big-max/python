#!/usr/bin/env python
# -*- coding:utf-8 -*-
import demjson
import json
from pymongo import MongoClient
mongoinfo = {"host":"127.0.0.1","port":"27017","user":"","password":"","dbname":"ams"}
#mongoinfo = {"host":"10.28.0.235","port":"27017","user":"","password":"","dbname":"ams"}
TIME_FORMAT='%Y-%m-%d %H:%M:%S'
# return a entity of mongodb
def db():
    global mongoinfo
    dbhost = mongoinfo['host']
    dbport = mongoinfo['port']
    dbuser = mongoinfo['user']
    dbpwd  = mongoinfo['password']
    dbname = mongoinfo['dbname']
    uri = 'mongodb://%s:%s'%(dbhost,dbport)
    client = MongoClient(uri)
    db = client.ams    
    return db



# values is a dict
def InsertPlaybooksDB(values):
    global mongoinfo
    dbhost = mongoinfo['host']
    dbport = mongoinfo['port']
    dbuser = mongoinfo['user']
    dbpwd  = mongoinfo['password']
    dbname = mongoinfo['dbname']
    uri = 'mongodb://%s:%s'%(dbhost,dbport)
    client = MongoClient(uri)
    db = client.ams
    db.playbooks.insert(values)

def InsertPlaysDB(values):
    global mongoinfo
    dbhost = mongoinfo['host']
    dbport = mongoinfo['port']
    dbuser = mongoinfo['user']
    dbpwd  = mongoinfo['password']
    dbname = mongoinfo['dbname']
    uri = 'mongodb://%s:%s'%(dbhost,dbport)
    client = MongoClient(uri)
    db = client.ams
    db.plays.insert(values)

def InsertTasksDB(values):
    global mongoinfo
    dbhost = mongoinfo['host']
    dbport = mongoinfo['port']
    dbuser = mongoinfo['user']
    dbpwd  = mongoinfo['password']
    dbname = mongoinfo['dbname']
    uri = 'mongodb://%s:%s'%(dbhost,dbport)
    client = MongoClient(uri)
    db = client.ams
    db.tasks.insert(values)

def UpdateLog(values):
    global mongoinfo
    dbhost = mongoinfo['host']
    dbport = mongoinfo['port']
    dbuser = mongoinfo['user']
    dbpwd  = mongoinfo['password']
    dbname = mongoinfo['dbname']
    uri = 'mongodb://%s:%s'%(dbhost,dbport)
    client = MongoClient(uri)
    db = client.ams
    db.playbook.update({"_id":jobid},{'$set':values})
    print (values)
