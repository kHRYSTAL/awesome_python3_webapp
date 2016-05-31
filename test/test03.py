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
from www.models import User
from www import orm


@asyncio.coroutine
def test(loop):
    yield from orm.create_pool(loop=loop, user='www-data', password='www-data', db='awesome')
    u=User(name='kHRYSTAL', email='khrystal0918@qq.com', passwd='yyg1990918', image='about:blank')
    yield from u.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))

if __name__ == '__main__':
    pass