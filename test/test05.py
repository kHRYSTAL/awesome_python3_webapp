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
@file: test05.py
@time: 16/6/1 上午3:18
"""
import asyncio
import hashlib

from www import orm
from www.models import User, next_id



@asyncio.coroutine
def test(loop):
    yield from orm.create_pool(loop=loop, user='www-data', password='www-data', database='awesome')
    u=User(name='Yao', email='jessica@qq.com', passwd="sas", image='about:blank')
    yield from u.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
