#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import zmq


from namekox_core.core.friendly import AsLazyProperty, ignore_exception
from namekox_websocket.constants import WEBSOCKET_CONFIG_KEY, DEFAULT_WSSBRIDGE_PUB_ADDR


class WssProxy(object):
    def __init__(self, sender):
        self.sender = sender

    def push(self, channel, message):
        data = (channel, message)
        self.sender.send_pyobj(data)

    def close(self):
        ignore_exception(self.sender.close)


class WssBridge(object):
    def __init__(self, config):
        self.config = config
        self._init()

    def _init(self):
        config = self.config.get(WEBSOCKET_CONFIG_KEY, {}) or {}
        self.pub_addr = config.get('pub_addr', DEFAULT_WSSBRIDGE_PUB_ADDR) or DEFAULT_WSSBRIDGE_PUB_ADDR
        websocket_ctx = zmq.Context()
        self.pub_sock = websocket_ctx.socket(zmq.PUB)
        self.pub_sock.setsockopt(zmq.HEARTBEAT_IVL, 2000)
        self.pub_sock.connect(self.pub_addr)

    @classmethod
    def name(cls):
        return 'wssbridge'

    @AsLazyProperty
    def proxy(self):
        return WssProxy(self.pub_sock)
