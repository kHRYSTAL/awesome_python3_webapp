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
@file: test03.py
@time: 16/5/31 下午2:21
"""
import asyncio
import hashlib

from www.models import User, next_id
from www import orm


@asyncio.coroutine
def test(loop):
    yield from orm.create_pool(loop=loop, user='www-data', password='www-data', database='awesome')
    u=User(admin=True, name='kHRYSTAL', email='jessicastam_love@163.com', passwd=hashlib.sha1(('%s:%s' % (next_id(), 'yyg1990918')).encode('utf-8')).hexdigest(), image='about:blank')
    yield from u.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))

if __name__ == '__main__':
    pass