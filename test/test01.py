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
@file: test01.py
@time: 16/5/31 上午1:36
"""
from www.models import User
from www.orm import Model, IntegerField, StringField

tableName = 'user'
primarykey = 'id'
fields = ['name', 'age', 'grade']
m = map(lambda f: '`%s`' % f, fields)
print(m)
escaped_fields = list(m)
print(escaped_fields)

sql = 'select `%s`, %s from `%s`' % (primarykey, ', '.join(escaped_fields), tableName)
print(sql)


matt = User(name='kHRYSTAL', email='khrystal0918@qq.com', passwd='yyg1990918', image='about:blank')
print(matt['passwd'],matt['name'],matt['email'])

if __name__ == '__main__':
    pass