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

from www import markdown2
from www.logger import logger
from aiohttp import web
from www.apis import APIError, Page, APIPermissionError, APIResourceNotFoundError
from www.apis import APIValueError
from www.config import configs
from www.coroweb import get, post
from www.models import User, Blog, next_id, Comment

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


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


#文本文件转换为html
def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


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


def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


# @get('/')
# @asyncio.coroutine
# def index(request):
#     summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
#     blogs = [
#         Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 120),
#         Blog(id='2', name='Something New', summary=summary, created_at=time.time() - 3600),
#         Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time() - 7200)
#     ]
#     return {
#         '__template__': 'blogs.html',
#         'blogs': blogs
#     }

@get('/')
@asyncio.coroutine
def index(*, page='1'):
    page_index = get_page_index(page)
    num = yield from Blog.findNumber('count(id)')
    # 如果没有数量或数量等于0 不显示
    if (not num) and num==0:
        logger.info('the type of num is: %s' % type(num))
        blogs = []
    else:
        # 通过page类计算当前页面的相关信息
        page = Page(num, page_index)
        blogs = yield from Blog.findAll(orderBy='created_at desc',limit=(page.offset, page.limit))

    return {
        '__template__': 'blogs.html',
        'page': page,
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
    # sha1 = hashlib.sha1()
    # sha1.update(user.id.encode('utf-8'))
    # sha1.update(b':')
    # sha1.update(passwd.encode('utf-8'))
    browser_sha1_passwd = '%s:%s' % (user.id, passwd)
    browser_sha1 = hashlib.sha1(browser_sha1_passwd.encode('utf-8'))
    logger.warn('user password: '+user.passwd)
    logger.warn('server password: '+browser_sha1.hexdigest())
    if user.passwd != browser_sha1.hexdigest():
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

'''
============================manage users==========================
'''




@get('/api/users')
@asyncio.coroutine
def api_get_users(request):
    users = yield from User.findAll(orderBy='created_at desc')
    for u in users:
        u.passwd = '******'
    return dict(users=users)


@get('/manage/users')
@asyncio.coroutine
def manage_users(*, page='1'):
    return {
        '__template__': 'manage_users.html',
        'page_index': get_page_index(page)
    }


'''
============================manage blog===========================
'''


@get('/manage/blogs/create')
@asyncio.coroutine
def mamage_create_blog():
    # write blog
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs'  # 提交到此接口
    }


@get('/manage/blogs')
@asyncio.coroutine
def manage_blogs(*, page = '1'):
    return {
        '__template__': "manage_blogs.html",
        'page_index': get_page_index(page)
    }


@get('/api/blogs')
@asyncio.coroutine
def api_blogs(*, page = '1'):
    page_index = get_page_index(page)
    blog_count = yield from Blog.findNumber('count(id)')
    p = Page(blog_count, page_index)
    if blog_count == 0:
        return dict(page = p, blogs = [])
    blogs = yield from Blog.findAll(orderBy = 'created_at desc', limit = (p.offset, p.limit))
    return dict(page = p, blogs = blogs)


@post('/api/blogs')
@asyncio.coroutine
def api_create_blog(request, *, name, summary, content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty')

    blog = Blog(user_id = request.__user__.id, user_name = request.__user__.name, user_image = request.__user__.image, name = name.strip(), summary = summary.strip(), content = content.strip())
    yield from blog.save()
    return blog


@get('/blog/{id}')
@asyncio.coroutine
def get_blog(id):
    blog = yield from Blog.find(id)
    comments = yield from Comment.findAll('blog_id=?', [id], orderBy = 'created_at desc')
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)

    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments
    }


@get('/api/blogs/{id}')
@asyncio.coroutine
def api_get_blog(*, id):
    blog = yield from Blog.find(id)
    return blog


@post('/api/blogs/{id}/delete')
@asyncio.coroutine
def api_delete_blog(id, request):
    logger.info("删除博客的博客ID为：%s" % id)
    check_admin(request)
    b = yield from Blog.find(id)
    if b is None:
        raise APIResourceNotFoundError('Comment')
    yield from b.remove()
    return dict(id=id)


@post('/api/blogs/modify')
@asyncio.coroutine
def api_modify_blog(request, *, id, name, summary, content):
    logger.info("修改的博客的博客ID为：%s", id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty')

    blog = yield from Blog.find(id)
    blog.name = name
    blog.summary = summary
    blog.content = content

    yield from blog.update()
    return blog


@get('/manage/blogs/modify/{id}')
@asyncio.coroutine
def manage_modify_blog(id):
    return {
        '__template__': 'manage_blog_modify.html',
        'id': id,
        'action': '/api/blogs/modify'
    }

'''
============================manage comment===========================
'''


@get('/manage/')
@asyncio.coroutine
def manage():
    return 'redirect:/manage/comments'


@get('/manage/comments')
@asyncio.coroutine
def manage_comments(*, page='1'):
    return {
        '__template__': 'manage_comments.html',
        'page_index': get_page_index(page)
    }


@get('/api/comments')
@asyncio.coroutine
def api_comments(*, page='1'):
    page_index = get_page_index(page)
    num = yield from Comment.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = yield from Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, comments=comments)


@post('/api/blogs/{id}/comments')
@asyncio.coroutine
def api_create_comment(id, request, *, content):
    user = request.__user__
    if user is None:
        raise APIPermissionError('content')
    if not content or not content.strip():
        raise APIValueError('content')
    blog = yield from Blog.find(id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name,
                      user_image=user.image, content=content.strip())
    yield from comment.save()
    return comment


@post('/api/comments/{id}/delete')
@asyncio.coroutine
def api_delete_comments(id, request):
    check_admin(request)
    c = yield from Comment.find(id)
    if c is None:
        raise APIResourceNotFoundError('Comment')
    yield from c.remove()
    return dict(id=id)

if __name__ == '__main__':
    pass