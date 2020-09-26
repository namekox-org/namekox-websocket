#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import os
import zmq
import zmq.auth


from namekox_core.core.friendly import ignore_exception
from namekox_websocket.constants import WEBSOCKET_CONFIG_KEY, DEFAULT_WSSBRIDGE_PUB_ADDR


class Proxy(object):
    def __init__(self, config):
        self.config = config
        self.pub_addr = None
        self.pub_sock = None
        self._init()

    def _init(self):
        config = self.config.get(WEBSOCKET_CONFIG_KEY, {}) or {}
        self.pub_addr = config.get('pub_addr', DEFAULT_WSSBRIDGE_PUB_ADDR) or DEFAULT_WSSBRIDGE_PUB_ADDR
        websocket_ctx = zmq.Context()
        self.pub_sock = websocket_ctx.socket(zmq.PUB)
        server_public_file = os.path.join('.', 'server.key')
        client_secret_file = os.path.join('.', 'client.key_secret')
        self.pub_sock.setsockopt(zmq.HEARTBEAT_IVL, 2000)
        client_public, client_secret = zmq.auth.load_certificate(client_secret_file)
        self.pub_sock.curve_secretkey = client_secret
        self.pub_sock.curve_publickey = client_public
        server_public, _ = zmq.auth.load_certificate(server_public_file)
        self.pub_sock.curve_serverkey = server_public
        self.pub_sock.connect(self.pub_addr)

    def push(self, channel, message):
        data = (channel, message)
        self.pub_sock.send_pyobj(data)

    def close(self):
        ignore_exception(self.pub_sock.close)
