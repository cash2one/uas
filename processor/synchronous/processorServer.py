#!/usr/bin/env python
# coding: utf8
# author: Maven
# datetime: 15 May 2012

from userRestfulProcessor import UserProcessor

import threading
import Pyro4
from tornado.options import define, options
import logging

define("running_pyro4_host", default="192.168.91.48", help="Pyro4 nameserver running host")
define("running_pyro4_port", default=9999, help="Pyro4 nameserver running port", type=int)

define("running_service_host", default="192.168.248.21", help="Service Running host")

#start processor server
if __name__ == "__main__":

    logging.basicConfig(
            level = logging.DEBUG,
            filename = 'processorServer.log',
            filemode = 'w',
            )
    logging.info('processor server start...')

    Pyro4.config.HOST = options.running_service_host
    Pyro4.config.NS_HOST = options.running_pyro4_host
    Pyro4.config.NS_PORT = options.running_pyro4_port

    Pyro4.Daemon.serveSimple(
          {
            UserProcessor(): "user_processor",
        },
        ns=True, verbose=True)
    logging.info('processor server started, running')
