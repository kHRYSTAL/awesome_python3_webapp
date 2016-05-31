#!/usr/bin/env python3
# -*- coding:utf-8 -*-


"""
@version: ??
@usage: define API Exception
@author: kHRYSTAL
@license: Apache Licence 
@contact: khrystal0918@gmail.com
@site: https://github.com/kHRYSTAL
@software: PyCharm
@file: apis.py
@time: 16/5/31 下午5:25
"""


class APIError(Exception):
    '''
    the base APIError which contains error(required), data(optional) and message(optional).
    '''
    def __init__(self, error, field='', message=''):
        super(APIError, self).__init__(message)
        self.error = error
        self.field = field
        self.message = message


class APIValueError(APIError):
    '''
    Indicate the input value has error or invalid. The data specifies the error field of input form.
    '''
    def __init__(self, field, message=''):
        super(APIValueError, self).__init__('value:invalid', field, message)

class APIResourceNotFoundError(APIError):
    '''
    Indicate the resource was not found. The data specifies the resource name.
    '''
    def __init__(self, field, message=''):
        super(APIResourceNotFoundError, self).__init__('value:notfound', field, message)

class APIPermissionError(APIError):
    '''
    Indicate the api has no permission.
    '''
    def __init__(self, message=''):
        super(APIPermissionError, self).__init__('permission:forbidden', 'permission', message)