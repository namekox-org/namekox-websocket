#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import six
import json


class WssMessage(object):
    def __init__(self, data=None, errs=''):
        self.errs = errs
        self.data = data

    def as_json(self):
        msg = {
            'errs': self.errs,
            'data': self.data,
        }
        msg = json.dumps(msg)
        return six.text_type(msg)
