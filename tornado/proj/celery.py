#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import absolute_import
from celery import Celery
from celery import Celery, platforms
platforms.C_FORCE_ROOT = True
app = Celery('proj', include=['proj.tasks'])
app.config_from_object('proj.config')
#CELERY_ENABLE_UTC = False
#lapp.conf.timezone = 'CST'
app.conf.timezone = 'Asia/Beijing'
if __name__ == '__main__':
    app.start()
