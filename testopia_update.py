#!/usr/bin/env python

import sys
import argparse
import logging
import ConfigParser

from external.testopia import Testopia

class Options(object):
    pass

class ArgumentsHandler(object):
    def __init__(self, testopia, opts, logger, config):
        self.testopia = testopia
        self.logger = logger
        self.opts = opts
        self.config = config

    def list_products(self):
        print "HERE"
        pass

def get_args():
    parser = argparse.ArgumentParser(description="Update testopia script.")

    parser.add_argument('--config', dest="config", required=False,
        help='Configuration file.')
    parser.add_argument('--host', dest="host", required=False,
        help='URL of Testopia instance.')
    parser.add_argument('--username', dest="username", required=False,
        help='Username of Testopia instance.')
    parser.add_argument('--password', dest="password", required=False,
        help='Password of Testopia instance.')

    parser.add_argument('--list-products', required=False, action="store_true",
        dest="list_products", default=False, help='List available products.')
    parser.add_argument('--verbose', required=False, action="store_true",
        dest="verbose", default=False, help='Enable verbose mode.')
    parser.add_argument('--debug', required=False, action="store_true",
        dest="debug", default=False, help='Enable debug mode.')

    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    logger = None
    opts = Options()

    if args.verbose or args.debug:
        logging.basicConfig(stream=sys.stdout)
        root = logging.getLogger()
        root.setLevel(logging.DEBUG if args.debug else logging.INFO)
    else:
        logging.basicConfig(stream=sys.stderr)
    logger = logging.getLogger()

    config = None
    testopia_opts = ['host', 'username', 'password']
    if args.config:
        config = ConfigParser.SafeConfigParser()
        config.read(args.config)

        for to in testopia_opts:
            setattr(opts, to, config.get("Testopia", to))
    for to in testopia_opts:
        if to in vars(args):
            arg = getattr(args, to)
            if arg:
                setattr(opts, to, arg)

    args_handler = ArgumentsHandler(None, opts, logger, config)
    for arg in vars(args):
        if getattr(args, arg):
            m = getattr(args_handler, arg)
            m()
