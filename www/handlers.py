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
@file: handlers.py
@time: 16/5/31 下午6:49
"""
import hashlib
import json
import logging
import re
import asyncio
import time
from aiohttp import web
from www.apis import APIError
from www.apis import APIValueError
from www.config import configs
from www.coroweb import get, post
from www.models import User, Blog, next_id


COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

'''
@get('/')
@asyncio.coroutine
# 制定url是'/'的处理函数为index
def index(request):
    users = yield from User.findAll()
    return{
    '__template__': 'test.html',
    'users': users
    #'__template__'指定的模板文件是test.html，其他参数是传递给模板的数据
    }
'''
'''
@get('/api/users')
@asyncio.coroutine
def api_get_users(*, page = '1'):
    page_index = get_page_index(page)
    # 获取到要展示的博客页数是第几页
    user_count = yield from User.findNumber('count(id)')
    # count为MySQL中的聚集函数，用于计算某列的行数
    # user_count代表了有多个用户id
    p = Page(user_count, page_index, page_size = 2)
    # 通过Page类来计算当前页的相关信息, 其实是数据库limit语句中的offset，limit
    if user_count == 0:
        return dict(page = p, users = ())
    else:
    users = yield from User.findAll(orderBy = 'created_at desc', limit = (p.offset, p.limit))
    # page.offset表示从那一行开始检索，page.limit表示检索多少行
    for u in users:
    u.passwd = '******************'
    return dict(page = p, users = users)
'''


def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


@asyncio.coroutine
def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = yield from User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


@get('/')
@asyncio.coroutine
def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time() - 3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time() - 7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }


'''
============================login and register===========================
'''


@get('/register')
@asyncio.coroutine
def register():
    return {
        '__template__': 'register.html'
    }


@get('/signin')
@asyncio.coroutine
def signin():
    return {
        '__template__': 'signin.html'
    }


@get('/signout')
@asyncio.coroutine
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r


@post('/api/authenticate')
@asyncio.coroutine
def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    users = yield from User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@post('/api/users')
@asyncio.coroutine
def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = yield from User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    yield from user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

if __name__ == '__main__':
    pass