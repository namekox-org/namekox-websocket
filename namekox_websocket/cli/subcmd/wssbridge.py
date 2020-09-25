#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import os
import zmq
import zmq.auth


from functools import partial
from logging import getLogger
from zmq.devices import Device
from namekox_core.cli.subcmd.base import BaseCommand
from namekox_core.core.friendly import ignore_exception
from namekox_websocket.constants import WSSBRIDGE_CONFIG_KEY, DEFAULT_WSSBRIDGE_PUB_ADDR, DEFAULT_WSSBRIDGE_SUB_ADDR


logger = getLogger(__name__)


class WssZmqDevice(Device):
    def _setup_sockets(self):
        ctx = self.context_factory()

        self._context = ctx

        # create the sockets
        ins = ctx.socket(self.in_type)
        if self.out_type < 0:
            outs = ins
        else:
            outs = ctx.socket(self.out_type)
        server_secret_file = os.path.join('.', 'server.key_secret')
        server_public, server_secret = zmq.auth.load_certificate(server_secret_file)
        outs.curve_secretkey = server_secret
        outs.curve_publickey = server_public
        outs.curve_server = True
        # set sockopts (must be done first, in case of zmq.IDENTITY)
        for opt, value in self._in_sockopts:
            ins.setsockopt(opt, value)
        for opt, value in self._out_sockopts:
            outs.setsockopt(opt, value)

        for iface in self._in_binds:
            ins.bind(iface)
        for iface in self._out_binds:
            outs.bind(iface)

        for iface in self._in_connects:
            ins.connect(iface)
        for iface in self._out_connects:
            outs.connect(iface)

        return ins, outs


class WssBridgeRunner(object):
    def __init__(self, pub_addr=None, sub_addr=None, **kwargs):
        self.pub_addr = pub_addr
        self.sub_addr = sub_addr

    def start(self):
        device = WssZmqDevice(zmq.FORWARDER, zmq.PUB, zmq.SUB)
        device.bind_in(self.sub_addr)
        device.setsockopt_out(zmq.SUBSCRIBE, '')
        msg = 'sub: bind on {}'.format(self.sub_addr)
        logger.debug(msg)
        device.bind_out(self.pub_addr)
        msg = 'pub: bind on {}'.format(self.pub_addr)
        logger.debug(msg)
        msg = 'run: client <-SUB-> bridge <-PUB-server'
        logger.debug(msg)
        device.start()

    def stop(self):
        zmq.Context().term()


class WssBridgeStart(BaseCommand):
    """ start zmq proxy server """
    @classmethod
    def name(cls):
        return 'start'

    @classmethod
    def init_parser(cls, parser, config=None):
        wssbridge_conf = config.get(WSSBRIDGE_CONFIG_KEY, {})
        wssbridge_pub = wssbridge_conf.get('pub_addr', DEFAULT_WSSBRIDGE_PUB_ADDR) or DEFAULT_WSSBRIDGE_PUB_ADDR
        wssbridge_sub = wssbridge_conf.get('sub_addr', DEFAULT_WSSBRIDGE_SUB_ADDR) or DEFAULT_WSSBRIDGE_SUB_ADDR
        parser.add_argument('-p', '--pub_addr', action='store',
                            default=wssbridge_pub,
                            help='specify websocket bridge pub addr')
        parser.add_argument('-s', '--sub_addr', action='store',
                            default=wssbridge_sub,
                            help='specify websocket bridge sub addr')
        return parser

    @classmethod
    def main(cls, args, config=None):
        wssbridge_conf = config.get(WSSBRIDGE_CONFIG_KEY, {})
        wssbridge_conf.update({'pub_addr': args.pub_addr, 'sub_addr': args.sub_addr})
        runner = WssBridgeRunner(**wssbridge_conf)
        ignore_exception(runner.start, exc_func=runner.stop, expected_exceptions=(KeyboardInterrupt,))()


class WssBridgeGenCert(BaseCommand):
    """ create zmq certificates """
    @classmethod
    def name(cls):
        return 'gencert'

    @classmethod
    def init_parser(cls, parser, config=None):
        parser.add_argument('-s', '--server', action='store',
                            default='server',
                            help='Specify wssbridge server keys name')
        parser.add_argument('-c', '--client', action='store',
                            default='client',
                            help='Specify wssbridge client keys name')
        return parser

    @classmethod
    def main(cls, args, config=None):
        msg = None
        server_public_file = os.path.join('.', '{}.key'.format(args.server))
        server_secret_file = os.path.join('.', '{}.key_secret'.format(args.server))
        if not os.path.exists(server_public_file) and not os.path.exists(server_secret_file):
            zmq.auth.create_certificates('.', args.server)
        else:
            msg = '{0}.key or {0}.key_secret already exists, ignore'.format(args.server)
        msg and logger.warn(msg)
        client_public_file = os.path.join('.', '{}.key'.format(args.client))
        client_secret_file = os.path.join('.', '{}.key_secret'.format(args.client))
        if not os.path.exists(client_public_file) and not os.path.exists(client_secret_file):
            zmq.auth.create_certificates('.', args.client)
        else:
            msg = '{0}.key or {0}.key_secret already exists, ignore'.format(args.client)
        msg and logger.warn(msg)


class WssBridge(BaseCommand):
    """ start websocket bridge """
    @classmethod
    def name(cls):
        return 'wssbridge'

    @classmethod
    def init_parser(cls, parser, config=None):
        sub_parsers = parser.add_subparsers()
        sub_commands = [WssBridgeStart, WssBridgeGenCert]
        for cmd in sub_commands:
            cmd_parser = sub_parsers.add_parser(cmd.name(), help=cmd.__doc__, description=cmd.__doc__)
            cmd_runner = partial(cmd.main, config=config)
            cmd_parser.set_defaults(main=cmd_runner)
            cmd.init_parser(cmd_parser, config=config)
        return parser

    @classmethod
    def main(cls, args, config=None):
        pass
