#! -*- coding: utf-8 -*-

# author: forcemain@163.com


from namekox_core.core.friendly import as_singleton_cls


@as_singleton_cls
class Storage(object):
    def __init__(self):
        self.subscriptions = {}

    def smembers(self, name):
        return self.subscriptions.get(name, set())

    def sadd(self, name, *values):
        self.subscriptions.setdefault(name, set())
        self.subscriptions[name].update(values)

    def srem(self, name, *values):
        self.subscriptions.get(name, set()).difference_update(values)
        not self.subscriptions.get(name, None) and self.subscriptions.pop(name, None)
