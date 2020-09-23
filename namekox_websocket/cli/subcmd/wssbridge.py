#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import zmq


from logging import getLogger
from zmq.devices import Device
from namekox_core.cli.subcmd.base import BaseCommand
from namekox_core.core.friendly import ignore_exception
from namekox_websocket.constants import WSSBRIDGE_CONFIG_KEY, DEFAULT_WSSBRIDGE_PUB_ADDR, DEFAULT_WSSBRIDGE_SUB_ADDR


logger = getLogger(__name__)


class WssBridgeRunner(object):
    def __init__(self, pub_addr=None, sub_addr=None, **kwargs):
        self.pub_addr = pub_addr
        self.sub_addr = sub_addr

    def start(self):
        device = Device(zmq.FORWARDER, zmq.PUB, zmq.SUB)
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


class WssBridge(BaseCommand):
    """ start websocket bridge """
    @classmethod
    def name(cls):
        return 'wssbridge'

    @classmethod
    def init_parser(cls, parser, config=None):
        wssbridge_conf = config.get(WSSBRIDGE_CONFIG_KEY, {})
        wssbridge_pub = wssbridge_conf.get('pub_addr', DEFAULT_WSSBRIDGE_PUB_ADDR) or DEFAULT_WSSBRIDGE_PUB_ADDR
        wssbridge_sub = wssbridge_conf.get('sub_addr', DEFAULT_WSSBRIDGE_SUB_ADDR) or DEFAULT_WSSBRIDGE_SUB_ADDR
        parser.add_argument('-p', '--pub', action='store',
                            default=wssbridge_pub,
                            help='Specify websocket bridge pub addr')
        parser.add_argument('-s', '--sub', action='store',
                            default=wssbridge_sub,
                            help='Specify websocket bridge sub addr')
        return parser

    @classmethod
    def main(cls, args, config=None):
        wssbridge_conf = config.get(WSSBRIDGE_CONFIG_KEY, {})
        wssbridge_conf.update({'pub_addr': args.pub, 'sub_addr': args.sub})
        runner = WssBridgeRunner(**wssbridge_conf)
        ignore_exception(runner.start, exc_func=runner.stop, expected_exceptions=(KeyboardInterrupt,))()
