# Install
```shell script
bash install.sh
```

# Example
> ping.py
```python
#! -*- coding: utf-8 -*-

# author: forcemain@163.com


from namekox_websocket.core.message import WspMessage
from namekox_websocket.core.entrypoints.app import app as wss_app
from namekox_webserver.core.entrypoints.app import app as web_app
from namekox_websocket.core.dependencies.wssbridge import WssBridge


class Ping(object):
    name = 'ping'
    bridge = WssBridge()

    @web_app.api('/', methods=['GET'])
    def web_pong(self, request):
        message = WspMessage(data={'web_pong': True})
        self.bridge.broadcast('ping', message)

    @wss_app.wss('/', methods=['GET'])
    def wss_pong(self, request, sock_id, data):
        self.bridge.hub.subscribe('ping', sock_id)
        return {'wss_pong': True}
```

# Running
> config.yaml
```yaml
CONTEXT:
  - namekox_websocket.cli.subctx.wssbridge:WssBridge
COMMAND:
  - namekox_websocket.cli.subcmd.wssbridge:WssBridge
WEBSERVER:
  host: 0.0.0.0
  port: 80
WSSBRIDGE:
  pub_addr: tcp://0.0.0.0:60001
  sub_addr: tcp://0.0.0.0:60002
WEBSOCKET:
  host: 0.0.0.0
  port: 8000
  pub_addr: tcp://127.0.0.1:60001
  sub_addr: tcp://127.0.0.1:60002
```

> namekox wssbridge --help
```
usage: namekox wssbridge [-h] {start,gencert} ...

manage websocket bridge

positional arguments:
  {start,gencert}
    start          start zmq proxy server
    gencert        create zmq certificates

optional arguments:
  -h, --help       show this help message and exit
```

> namekox wssbridge gencert
```shell script
2020-09-23 18:05:14,621 WARNING server.key or server.key_secret already exists, ignore
2020-09-23 18:05:14,621 WARNING client.key or client.key_secret already exists, ignore
```

> namekox wssbridge start
```shell script
2020-09-23 18:06:11,642 DEBUG sub: bind on tcp://0.0.0.0:60002
2020-09-23 18:06:11,642 DEBUG pub: bind on tcp://0.0.0.0:60001
2020-09-23 18:06:11,642 DEBUG run: client <-SUB-> bridge <-PUB-server
```

> namekox run ping
```shell script
2020-09-23 18:05:39,028 DEBUG load service classes from ping failed,
2020-09-23 18:05:39,295 DEBUG load container class from namekox_core.core.service.container:ServiceContainer
2020-09-23 18:05:39,296 DEBUG starting services ['ping']
2020-09-23 18:05:39,296 DEBUG starting service ping entrypoints [ping:namekox_websocket.core.entrypoints.app.handler.WebSocketHandler:wss_pong, ping:namekox_webserver.core.entrypoints.app.handler.ApiServerHandler:web_pong, ping:namekox_webserver.core.entrypoints.app.server.WebServer:server]
2020-09-23 18:05:39,298 DEBUG spawn manage thread handle ping:namekox_webserver.core.entrypoints.app.server:handle_connect(args=(), kwargs={}, tid=handle_connect)
2020-09-23 18:05:39,298 DEBUG service ping entrypoints [ping:namekox_websocket.core.entrypoints.app.handler.WebSocketHandler:wss_pong, ping:namekox_webserver.core.entrypoints.app.handler.ApiServerHandler:web_pong, ping:namekox_webserver.core.entrypoints.app.server.WebServer:server] started
2020-09-23 18:05:39,298 DEBUG starting service ping dependencies [ping:namekox_websocket.core.dependencies.wssbridge.WssBridge:bridge, ping:namekox_websocket.core.dependencies.wssbridge.server.WebSocketServer:server]
2020-09-23 18:05:39,301 DEBUG spawn manage thread handle ping:namekox_websocket.core.dependencies.wssbridge:_run(args=(), kwargs={}, tid=_run)
2020-09-23 18:05:39,302 DEBUG spawn manage thread handle ping:namekox_websocket.core.server:handle_connect(args=(), kwargs={}, tid=handle_connect)
2020-09-23 18:05:39,303 DEBUG service ping dependencies [ping:namekox_websocket.core.dependencies.wssbridge.WssBridge:bridge, ping:namekox_websocket.core.dependencies.wssbridge.server.WebSocketServer:server] started
2020-09-23 18:05:39,303 DEBUG services ['ping'] started
2020-09-23 18:05:57,282 DEBUG spawn manage thread handle ping:namekox_webserver.core.entrypoints.app.server:handle_request(args=(<eventlet.greenio.base.GreenSocket object at 0x102bd0f10>, ('127.0.0.1', 51000)), kwargs={}, tid=handle_request)
2020-09-23 18:05:57,287 DEBUG spawn worker thread handle ping:web_pong(args=(<Request 'http://127.0.0.1/' [GET]>,), kwargs={}, context={})
2020-09-23 18:05:57,288 DEBUG publish {'errs': '', 'data': {'web_pong': True}, 'succ': True, 'type': 'message'} to channel ping succ
127.0.0.1 - - [23/Sep/2020 18:05:57] "GET / HTTP/1.1" 200 237 0.006758
2020-09-23 18:06:01,546 DEBUG spawn manage thread handle ping:namekox_websocket.core.server:handle_request(args=(<eventlet.greenio.base.GreenSocket object at 0x102be7890>, ('127.0.0.1', 51073)), kwargs={}, tid=handle_request)
2020-09-23 18:06:01,683 DEBUG spawn worker thread handle ping:wss_pong(args=(<Request 'http://127.0.0.1:8000/' [GET]>, 'f70e3468-c5ab-4adc-8145-c8ae9d81bb55', u'New participant joined'), kwargs={}, context={})
2020-09-23 18:06:03,898 DEBUG spawn worker thread handle ping:web_pong(args=(<Request 'http://127.0.0.1/' [GET]>,), kwargs={}, context={})
2020-09-23 18:06:03,899 DEBUG publish {'errs': '', 'data': {'web_pong': True}, 'succ': True, 'type': 'message'} to channel ping succ
127.0.0.1 - - [23/Sep/2020 18:06:03] "GET / HTTP/1.1" 200 237 0.001295
2020-09-23 18:06:04,316 DEBUG spawn worker thread handle ping:web_pong(args=(<Request 'http://127.0.0.1/' [GET]>,), kwargs={}, context={})
2020-09-23 18:06:04,316 DEBUG publish {'errs': '', 'data': {'web_pong': True}, 'succ': True, 'type': 'message'} to channel ping succ
127.0.0.1 - - [23/Sep/2020 18:06:04] "GET / HTTP/1.1" 200 237 0.001653
2020-09-23 18:06:04,508 DEBUG spawn worker thread handle ping:web_pong(args=(<Request 'http://127.0.0.1/' [GET]>,), kwargs={}, context={})
2020-09-23 18:06:04,509 DEBUG publish {'errs': '', 'data': {'web_pong': True}, 'succ': True, 'type': 'message'} to channel ping succ
127.0.0.1 - - [23/Sep/2020 18:06:04] "GET / HTTP/1.1" 200 237 0.001142
2020-09-23 18:06:04,735 DEBUG spawn worker thread handle ping:web_pong(args=(<Request 'http://127.0.0.1/' [GET]>,), kwargs={}, context={})
2020-09-23 18:06:04,736 DEBUG publish {'errs': '', 'data': {'web_pong': True}, 'succ': True, 'type': 'message'} to channel ping succ
127.0.0.1 - - [23/Sep/2020 18:06:04] "GET / HTTP/1.1" 200 237 0.001438
2020-09-23 18:06:17,372 DEBUG spawn worker thread handle ping:web_pong(args=(<Request 'http://127.0.0.1/' [GET]>,), kwargs={}, context={})
2020-09-23 18:06:17,372 DEBUG publish {'errs': '', 'data': {'web_pong': True}, 'succ': True, 'type': 'message'} to channel ping succ
127.0.0.1 - - [23/Sep/2020 18:06:17] "GET / HTTP/1.1" 200 237 0.002698
2020-09-23 18:06:17,927 DEBUG spawn worker thread handle ping:web_pong(args=(<Request 'http://127.0.0.1/' [GET]>,), kwargs={}, context={})
2020-09-23 18:06:17,928 DEBUG publish {'errs': '', 'data': {'web_pong': True}, 'succ': True, 'type': 'message'} to channel ping succ
127.0.0.1 - - [23/Sep/2020 18:06:17] "GET / HTTP/1.1" 200 237 0.001537
2020-09-23 18:06:18,493 DEBUG spawn worker thread handle ping:web_pong(args=(<Request 'http://127.0.0.1/' [GET]>,), kwargs={}, context={})
2020-09-23 18:06:18,493 DEBUG publish {'errs': '', 'data': {'web_pong': True}, 'succ': True, 'type': 'message'} to channel ping succ
127.0.0.1 - - [23/Sep/2020 18:06:18] "GET / HTTP/1.1" 200 237 0.001643
2020-09-23 18:06:21,466 DEBUG spawn worker thread handle ping:web_pong(args=(<Request 'http://127.0.0.1/' [GET]>,), kwargs={}, context={})
2020-09-23 18:06:21,466 DEBUG publish {'errs': '', 'data': {'web_pong': True}, 'succ': True, 'type': 'message'} to channel ping succ
127.0.0.1 - - [23/Sep/2020 18:06:21] "GET / HTTP/1.1" 200 237 0.001566
2020-09-23 18:06:21,927 DEBUG spawn worker thread handle ping:web_pong(args=(<Request 'http://127.0.0.1/' [GET]>,), kwargs={}, context={})
2020-09-23 18:06:21,927 DEBUG publish {'errs': '', 'data': {'web_pong': True}, 'succ': True, 'type': 'message'} to channel ping succ
127.0.0.1 - - [23/Sep/2020 18:06:21] "GET / HTTP/1.1" 200 237 0.001147
2020-09-23 18:06:22,426 DEBUG spawn worker thread handle ping:web_pong(args=(<Request 'http://127.0.0.1/' [GET]>,), kwargs={}, context={})
2020-09-23 18:06:22,426 DEBUG publish {'errs': '', 'data': {'web_pong': True}, 'succ': True, 'type': 'message'} to channel ping succ
127.0.0.1 - - [23/Sep/2020 18:06:22] "GET / HTTP/1.1" 200 237 0.001243
^C2020-09-23 18:34:49,011 DEBUG stopping services ['ping']
2020-09-23 18:34:49,012 DEBUG stopping service ping entrypoints [ping:namekox_websocket.core.entrypoints.app.handler.WebSocketHandler:wss_pong, ping:namekox_webserver.core.entrypoints.app.handler.ApiServerHandler:web_pong, ping:namekox_webserver.core.entrypoints.app.server.WebServer:server]
2020-09-23 18:34:49,013 DEBUG wait service ping entrypoints [ping:namekox_websocket.core.entrypoints.app.handler.WebSocketHandler:wss_pong, ping:namekox_webserver.core.entrypoints.app.handler.ApiServerHandler:web_pong, ping:namekox_webserver.core.entrypoints.app.server.WebServer:server] stop
2020-09-23 18:34:49,013 DEBUG service ping entrypoints [ping:namekox_websocket.core.entrypoints.app.handler.WebSocketHandler:wss_pong, ping:namekox_webserver.core.entrypoints.app.handler.ApiServerHandler:web_pong, ping:namekox_webserver.core.entrypoints.app.server.WebServer:server] stopped
2020-09-23 18:34:49,013 DEBUG stopping service ping dependencies [ping:namekox_websocket.core.dependencies.wssbridge.WssBridge:bridge, ping:namekox_websocket.core.dependencies.wssbridge.server.WebSocketServer:server]
2020-09-23 18:34:49,014 DEBUG service ping dependencies [ping:namekox_websocket.core.dependencies.wssbridge.WssBridge:bridge, ping:namekox_websocket.core.dependencies.wssbridge.server.WebSocketServer:server] stopped
127.0.0.1 - - [23/Sep/2020 18:34:49] "GET / HTTP/1.1" 200 0 1727.465750
2020-09-23 18:34:49,017 DEBUG services ['ping'] stopped
2020-09-23 18:34:49,017 DEBUG killing services ['ping']
2020-09-23 18:34:49,017 DEBUG service ping already stopped
2020-09-23 18:34:49,018 DEBUG services ['ping'] killed
```

# Debug
> config.yaml
```yaml
CONTEXT:
  - namekox_websocket.cli.subctx.wssbridge:WssBridge
COMMAND:
  - namekox_websocket.cli.subcmd.wssbridge:WssBridge
WEBSERVER:
  host: 0.0.0.0
  port: 80
WSSBRIDGE:
  pub_addr: tcp://0.0.0.0:60001
  sub_addr: tcp://0.0.0.0:60002
WEBSOCKET:
  host: 0.0.0.0
  port: 8000
  pub_addr: tcp://127.0.0.1:60001
  sub_addr: tcp://127.0.0.1:60002
```

> namekox shell
```shell script
In [1]: nx.wssbridge.proxy.push(channel='ping', message={'nb': True})
```
