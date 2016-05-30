#!/usr/bin/env python3
# -*- coding:utf-8 -*-


"""
@version: ??
@usage: orm
@author: kHRYSTAL
@license: Apache Licence 
@contact: khrystal0918@gmail.com
@site: https://github.com/kHRYSTAL
@software: PyCharm
@file: orm.py
@time: 16/5/30 下午11:35
"""

import asyncio, logging
import aiomysql


def log(sql, args=()):
    logging.info('SQL: %s' % sql)


'''
创建连接池
连接池由全局变量__pool存储
使用连接池的好处是不必频繁地打开和关闭数据库连接，而是能复用就尽量复用。
'''
async def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global __pool
    #数据库连接池初始化 使用协程
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port',3306),
        user=kw['user'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit',True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )

'''
封装查询语句
sql: sql语句
args: 查询参数
size: 查询长度
'''
async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    # async with __pool.get()等同于 yield from __pool
    # 异步调用协程 目的是为了时间和线程上的优化
    async with __pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 自动替换占位符 校验参数是否为空 这样可以防止SQL注入攻击
            await cur.execute(sql.replace('?', '%s'), args or ())
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        logging.info('rows returned: %s' % len(rs))
        return rs


'''
INSERT、UPDATE、DELETE语句
sql: sql语句
return: 返回影响行数
'''
async def execute(sql, args):
    log(sql)
    async with __pool.get() as conn:
        try:
            cur = await conn.cursor()
            await cur.execute(sql.replace('?', '%s'), args)
            affected = cur.rowcount
            await cur.close()
        except BaseException as e:
            raise
        return affected


if __name__ == '__main__':
    pass