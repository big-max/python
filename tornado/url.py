#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
	@author:hujin
	@date:2016-3-8
	@desc:restful api url mapping , all urls defined here
'''
import sys
from handler.run import runHandler
from handler.loaddata import serversHandler
from handler.loaddata import tasksHandler,playbooksHandler
from handler.users import usersHandler
from handler.servers import srvHandler
from handler.fp import FpHandler
from handler.loaddata import dictHandler
from handler.errmsg import errmsgHandler
from handler.hdisks import hdisksHandler
from handler.checkserverstatus import  checkServerStatusHandler
from handler.checkserverstatus import  checkPlaybookStatusHandler
from healthCheck.job import JobHandler
from healthCheck.jobDetail import JobDetailHandler
from healthCheck.jobRunResult import JobRunResultHandler
from healthCheck.handlerHosts import HostsHandler
from healthCheck.iperrmsg import HealthchecherrmsgHandler
from configCompare.configJobs import ConfigJobHandler
from configCompare.configJobDetail import configJobDetailHandler
from configCompare.configJobRunResult import configJobRunResultHandler
from configCompare.compareConf import compareConfHandler
from configCompare.configConfHandler import configConfHandler
from configCompare.iperrmsg import configCompareerrmsgHandler
from logCatch.logCatch import logCatchHandler
from logCatch.logDownLoad import LogDownloadHandler
url=[
	(r'/api/v1/run',runHandler),
	(r'/api/v1/users',usersHandler),
        (r'/api/v1/servers',srvHandler),
        (r'/api/v1/fp',FpHandler),
	(r'/odata/servers',serversHandler),
        (r'/odata/tasks',tasksHandler),
        (r'/odata/playbooks',playbooksHandler),
        (r'/odata/dict',dictHandler),
        (r'/odata/errmsg',errmsgHandler),
        (r'/odata/healthcheckiperrmsg',HealthchecherrmsgHandler),
        (r'/odata/hdisks',hdisksHandler),
        (r'/api/v1/checkserverstatus',checkServerStatusHandler),
        (r'/api/v1/checkplaybookstatus',checkPlaybookStatusHandler),
        (r'/api/v1/jobs',JobHandler),
        (r'/api/v1/jobdetail',JobDetailHandler),
        (r'/api/v1/jobrunresult',JobRunResultHandler),
        (r'/api/v1/hosts',HostsHandler),
        (r'/api/v1/configJobs',ConfigJobHandler),
        (r'/api/v1/configjobdetail',configJobDetailHandler),
        (r'/api/v1/configjobrunresult',configJobRunResultHandler),
        (r'/api/v1/compareConf',compareConfHandler),
        (r'/api/v1/configcompareiperrmsg',configCompareerrmsgHandler),
        (r'/api/v1/getconfigInfo',configConfHandler),
        (r'/api/v1/logcatch',logCatchHandler),
        (r'/api/v1/logdownload',LogDownloadHandler),
    ]


