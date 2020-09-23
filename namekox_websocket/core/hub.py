#! -*- coding: utf-8 -*-

# author: forcemain@163.com


from namekox_core.core.friendly import as_singleton_cls


from .storage import Storage


@as_singleton_cls
class WebSocketHub(object):
    def __init__(self, server=None, storage=None):
        self.server = server
        self.sockets = {}
        self.storage = storage or Storage()

    def subscribe(self, channel, sock_id):
        self.storage.sadd(channel, sock_id)
        self.storage.sadd(sock_id, channel)

    def unsubscribe(self, channel, sock_id):
        self.storage.srem(channel, sock_id)
        self.storage.srem(sock_id, channel)
