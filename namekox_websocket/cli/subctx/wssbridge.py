#! -*- coding: utf-8 -*-

# author: forcemain@163.com


from namekox_websocket.core.proxy import Proxy


class WssBridge(object):
    def __init__(self, config):
        self.config = config
        self.proxy = Proxy(config)

    @classmethod
    def name(cls):
        return 'wssbridge'
