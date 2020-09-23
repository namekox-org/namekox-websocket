#! -*- coding: utf-8 -*-

# author: forcemain@163.com

from namekox_websocket.core.entrypoints.app import app


class Ping(object):
    name = 'ping'

    @app.wss('/')
    def pong(self):
        return {}
