#!/usr/bin/env python3
# -*- coding:utf-8 -*-


"""
@version: ??
@usage: async web application.
@author: kHRYSTAL
@license: Apache Licence 
@contact: khrystal0918@gmail.com
@site: https://github.com/kHRYSTAL
@software: PyCharm
@file: app.py
@time: 16/5/30 下午10:57
"""

import logging; logging.basicConfig(level=logging.INFO,
                    format='levelname:%(levelname)s filename: %(filename)s '
                           'outputNumber: [%(lineno)d]  thread: %(threadName)s output msg:  %(message)s'
                           ' - %(asctime)+8s', datefmt='[%d/%b/%Y %H:%M:%S]',
                    filename='./loggmsg.log',
                    filemode='a')

import asyncio, os, json, time
from datetime import datetime
from aiohttp import web


def index(request):
    return web.Response(body=b'<h1>Awesome</h1>',content_type='text/html')


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server start at http://127.0.0.1:9000...')
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()

if __name__ == '__main__':
    pass