#! -*- coding: utf-8 -*-

# author: forcemain@163.com


from namekox_websocket.core.server import BaseWebSocketServer
from namekox_core.core.service.entrypoint import EntrypointProvider


class WebSocketServer(BaseWebSocketServer, EntrypointProvider):
    pass
