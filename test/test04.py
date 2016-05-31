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
@file: test04.py
@time: 16/5/31 下午8:03
"""
from www.models import User


def getUsers():
    users = yield from User.findAll()
    print(users)


if __name__ == '__main__':
    pass