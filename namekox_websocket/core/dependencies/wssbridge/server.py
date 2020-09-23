#! -*- coding: utf-8 -*-

# author: forcemain@163.com


from namekox_websocket.core.server import BaseWebSocketServer
from namekox_core.core.service.dependency import DependencyProvider


class WebSocketServer(BaseWebSocketServer, DependencyProvider):
    pass
