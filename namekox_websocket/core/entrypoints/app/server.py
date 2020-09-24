#! -*- coding: utf-8 -*-

# author: forcemain@163.com


from namekox_websocket.core.server import BaseWssServer
from namekox_core.core.service.entrypoint import EntrypointProvider


class WssServer(BaseWssServer, EntrypointProvider):
    pass
