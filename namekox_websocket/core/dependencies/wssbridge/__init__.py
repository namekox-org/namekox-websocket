#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import eventlet.green.zmq as zmq


from logging import getLogger
from namekox_websocket.core.hub import WebSocketHub
from namekox_core.core.spawning import SpawningProxy
from namekox_core.core.friendly import ignore_exception
from namekox_core.core.service.dependency import Dependency
from namekox_websocket.core.message import WssMessage, WspMessage
from namekox_websocket.constants import WEBSOCKET_CONFIG_KEY, DEFAULT_WEBSOCKET_PUB_ADDR, DEFAULT_WEBSOCKET_SUB_ADDR


from .server import WebSocketServer


logger = getLogger(__name__)


class WssBridge(Dependency):
    server = WebSocketServer()

    def __init__(self, *args, **kwargs):
        self.gt = None
        self.hub = None
        self.accpted = True
        self.pub_addr = None
        self.sub_addr = None
        self.pub_sock = None
        self.sub_sock = None
        super(WssBridge, self).__init__(*args, **kwargs)

    def setup(self):
        self.hub = WebSocketHub(server=self, storage=self.server.hub_storage)
        config = self.container.config.get(WEBSOCKET_CONFIG_KEY, {})
        self.pub_addr = config.get('pub_addr', DEFAULT_WEBSOCKET_PUB_ADDR) or DEFAULT_WEBSOCKET_PUB_ADDR
        self.sub_addr = config.get('sub_addr', DEFAULT_WEBSOCKET_SUB_ADDR) or DEFAULT_WEBSOCKET_SUB_ADDR
        websocket_ctx = zmq.Context()
        self.pub_sock = websocket_ctx.socket(zmq.PUB)
        self.sub_sock = websocket_ctx.socket(zmq.SUB)
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, '')

    def start(self):
        self.pub_sock.setsockopt(zmq.HEARTBEAT_IVL, 2000)
        self.pub_sock.connect(self.pub_addr)
        self.sub_sock.setsockopt(zmq.HEARTBEAT_IVL, 2000)
        self.sub_sock.connect(self.sub_addr)
        self.gt = self.container.spawn_manage_thread(self._run)

    def _run(self):
        while self.accpted:
            channel, message = self.sub_sock.recv_pyobj()
            sockids = self.server.hub.storage.smembers(channel)
            sockets = []
            for sock_id in sockids:
                sock = self.server.hub.sockets.get(sock_id, None)
                sock and sockets.append(sock)
            channel, message = WssMessage(
                channel=channel,
                message=message,
            ).serialize()
            SpawningProxy(sockets).send(message)

    def stop(self):
        self.accpted = False
        pub_sock_close = ignore_exception(self.pub_sock.close)
        pub_sock_close()
        sub_sock_close = ignore_exception(self.sub_sock.close)
        sub_sock_close()
        self.gt.kill()

    def broadcast(self, channel, message):
        succ_msg = None
        if not isinstance(message, WspMessage):
            fail_msg = 'message {} no isinstance of {}, ignore'.format(message, WspMessage)
            logger.warn(fail_msg)
        else:
            message = message.as_dict()
            self.pub_sock.send_pyobj((channel, message))
            succ_msg = 'publish {} to channel {} succ'.format(message, channel)
        succ_msg and logger.debug(succ_msg)
