#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import os
import eventlet
import werkzeug


from uuid import UUID
from werkzeug import Request
from logging import getLogger
from eventlet import wsgi, wrap_ssl
from werkzeug.routing import Rule, Map
from namekox_core.core.friendly import ignore_exception
from namekox_core.core.loaders import import_dotpath_class
from namekox_core.core.service.extension import SharedExtension, ControlExtension
from namekox_websocket.constants import WEBSOCKET_CONFIG_KEY, DEFAULT_WEBSOCKET_HOST, DEFAULT_WEBSOCKET_PORT


from .hub import WebSocketHub


logger = getLogger(__name__)


class WsgiApp(object):
    def __init__(self, server):
        self.server = server
        self.urlmap = server.gen_urls_map()

    def __call__(self, environ, start_response):
        request = Request(environ)
        adapter = self.urlmap.bind_to_environ(environ)
        try:
            entrypoint, pvalues = adapter.match()
            request.path_values = pvalues
            response = entrypoint.handle_request(request)
        except werkzeug.exceptions.HTTPException as e:
            response = e
        return response(environ, start_response)


class BaseWssServer(SharedExtension, ControlExtension):
    SSL_ARGS = [
        'keyfile', 'certfile', 'server_side', 'cert_reqs',
        'ssl_version', 'ca_certs',
        'do_handshake_on_connect', 'suppress_ragged_eofs',
        'ciphers'
    ]

    def __init__(self, *args, **kwargs):
        self.gt = None
        self.hub = None
        self.host = None
        self.port = None
        self.ev_sock = None
        self.ev_serv = None
        self.accpted = True
        self.sslargs = None
        self.srvargs = None
        self.started = False
        self.middlewares = None
        self.hub_storage = kwargs.get('hub_storage', None)
        super(BaseWssServer, self).__init__(*args, **kwargs)

    def setup(self):
        if self.host is not None and self.port is not None and self.sslargs is not None and self.srvargs is not None:
            return
        self.hub = WebSocketHub(server=self, storage=self.hub_storage)
        config = self.container.config.get(WEBSOCKET_CONFIG_KEY, {}).copy()
        self.middlewares = config.pop('middlewares', []) or []
        self.host = config.pop('host', DEFAULT_WEBSOCKET_HOST) or DEFAULT_WEBSOCKET_HOST
        self.port = config.pop('port', DEFAULT_WEBSOCKET_PORT) or DEFAULT_WEBSOCKET_PORT
        self.sslargs = {k: config.pop(k) for k in config if k in self.SSL_ARGS}
        self.sslargs and self.sslargs.update({'server_side': True})
        self.srvargs = config
        self.srvargs.pop('pub_addr', None)
        self.srvargs.pop('sub_addr', None)

    def start(self):
        if not self.started:
            self.started = True
            self.ev_sock = eventlet.listen((self.host, self.port))
            self.ev_sock.settimeout(None)
            self.ev_serv = self.get_wsgi_srv()
            self.gt = self.container.spawn_manage_thread(self.handle_connect)

    def stop(self):
        self.accpted = False
        self.gt.kill()
        self.ev_sock.close()

    def add_websocket(self, ws_sock):
        sock_id = str(UUID(bytes=os.urandom(16), version=4))
        self.hub.sockets[sock_id] = ws_sock
        return sock_id

    def del_websocket(self, sock_id):
        channel = self.hub.storage.smembers(sock_id)
        for c in list(channel):
            self.hub.unsubscribe(c, sock_id)
            self.hub.unsubscribe(sock_id, c)
        ws_sock = self.hub.sockets.pop(sock_id, None)
        ws_sock and ignore_exception(ws_sock.close)()

    def handle_connect(self):
        while self.accpted:
            sock, addr = self.ev_sock.accept()
            sock.settimeout(self.ev_serv.socket_timeout)
            self.container.spawn_manage_thread(self.handle_request, args=(sock, addr))

    def handle_request(self, sock, addr):
        connection = [addr, sock, wsgi.STATE_IDLE]
        self.ev_serv.process_request(connection)

    def apply_addons(self, app):
        for mid_cls_path in self.middlewares:
            msg = 'load middleware objects from {} failed, '
            err, mid_cls = import_dotpath_class(mid_cls_path)
            log = False
            if err is not None:
                log = True
                msg += err
            log and logger.warn(msg.format(mid_cls_path))
            if mid_cls is None:
                continue
            fun = mid_cls(app)
            app = fun(self)
        return app

    def get_wsgi_app(self):
        app = WsgiApp(self)
        return self.apply_addons(app)

    def get_wsgi_srv(self):
        sock = self.ev_sock if not self.sslargs else wrap_ssl(self.ev_sock, **self.sslargs)
        addr = self.ev_sock.getsockname()
        return wsgi.Server(sock, addr, self.get_wsgi_app(), **self.srvargs)

    def gen_urls_map(self):
        url_map = Map()
        for extension in self.extensions:
            rule = getattr(extension, 'url_rule', None)
            if not isinstance(rule, Rule):
                continue
            url_map.add(rule)
        return url_map

    @staticmethod
    def get_context_from_header(request):
        # TODO: headers to context
        return {}
