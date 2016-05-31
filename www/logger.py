#!/usr/bin/env python3
# -*- coding:utf-8 -*-


"""
@version: ??
@usage: 
@author: kHRYSTAL
@license: Apache Licence 
@contact: khrystal0918@gmail.com
@site: https://github.com/kHRYSTAL
@software: PyCharm
@file: logger.py
@time: 16/5/31 下午4:20
"""

# import logging; logging.basicConfig(level=logging.INFO, filename='server_info.log')
import logging
import logging.handlers

LOG_FILE = '../log/server_info.log'

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024) # 实例化handler
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

formatter = logging.Formatter(fmt)   # 实例化formatter
handler.setFormatter(formatter)      # 为handler添加formatter

logger = logging.getLogger('server_info')    # 获取名为server_info的logger
logger.addHandler(handler)           # 为logger添加handler
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    pass