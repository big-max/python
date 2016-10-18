#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import logging.config
CONF_LOG = "/opt/tornado/conf/logging.conf"
def log():
    logging.config.fileConfig(CONF_LOG)
    logger = logging.getLogger("tornado")
    return logger

