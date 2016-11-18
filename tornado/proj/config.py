#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import absolute_import

CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/5'
BROKER_URL = 'redis://127.0.0.1:6379/6'
from datetime import timedelta
#app.conf.timezone = 'UTC'
TIME_ZONE='UTC'
from kombu import Exchange, Queue
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('queue_deploy_run_playbook', Exchange('queue_deploy_run_playbook'), routing_key='queue_deploy_run_playbook'),
    Queue('queue_healthCheck_run_playbook', Exchange('queue_healthCheck_run_playbook'), routing_key='queue_healthCheck_run_playbook'),
    Queue('queue_configCompare_run_playbook', Exchange('queue_configCompare_run_playbook'), routing_key='queue_configCompare_run_playbook'),
    Queue('queue_logCatch_run_playbook', Exchange('queue_logCatch_run_playbook'), routing_key='queue_logCatch_run_playbook'),
)

class MyRouter(object):
      def route_for_task(self,task,args=None,kwargs=None):
          if task.startswith('proj.tasks.deploy'):
             return {'queue':'queue_deploy_run_playbook'}
          elif task.startswith('proj.tasks.healthCheck'):
             return {'queue':'queue_healthCheck_run_playbook'}
          elif task.startswith('proj.tasks.configCompare'):
             return {'queue':'queue_configCompare_run_playbook'}
          elif task.startswith('proj.tasks.logCatch'):
             return {'queue':'queue_logCatch_run_playbook'}
          else: # default queue
             return None  

CELERY_ROUTES = (MyRouter(), )
