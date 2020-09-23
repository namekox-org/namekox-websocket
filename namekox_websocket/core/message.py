#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import six
import json


class WssMessage(object):
    def __init__(self, channel=None, message=None):
        self.channel = channel
        self.message = message

    def serialize(self):
        channel = self.channel
        message = json.dumps(self.message)
        message = six.text_type(message)
        return channel, message


class WspMessage(object):
    def __init__(self, type='message', succ=True, errs='', data=None):
        self.type = type
        self.succ = succ
        self.errs = errs
        self.data = data

    def as_dict(self):
        return {
            'type': self.type,
            'succ': self.succ,
            'errs': self.errs,
            'data': self.data,
        }
