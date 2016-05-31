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
@file: test02.py
@time: 16/5/31 下午1:44
"""
import time
import uuid

time_ = time.time() * 1000
print(time_)
print('%015d' % time_)
uuid_ = uuid.uuid4()
print(uuid_)
print(uuid_.hex)



if __name__ == '__main__':
    pass