#!/usr/bin/env python

import os
import sys
import argparse
import logging
import ConfigParser
import types

from external.testopia import Testopia

DEFAULT_CONFIG_FILE = "testopia_update.config"

class Options(object):
    pass

class ArgumentsHandler(object):
    def __init__(self, testopia, opts, logger, config):
        self.testopia = testopia
        self.logger = logger
        self.opts = opts
        self.config = config

    def list_products(self):
        pass

def get_args():
    parser = argparse.ArgumentParser(description="Update testopia script.")

    parser.add_argument('--config', dest="config", required=False,
        help='Configuration file.')
    parser.add_argument('--url', dest="url", required=False,
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

    testopia_opts = ['url', 'username', 'password']

    config = None
    if not args.config and os.path.exists(DEFAULT_CONFIG_FILE):
        args.config = DEFAULT_CONFIG_FILE

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
        if not hasattr(opts, to):
            logger.error("%s: Requires testopia %s in arguments or config." % \
                (sys.argv[0], to))
            sys.exit(1)

    testopia = Testopia(opts.username, opts.password, opts.url, sslverify=False)
    args_handler = ArgumentsHandler(testopia, opts, logger, config)
    for arg in vars(args):
        if getattr(args, arg):
            m = getattr(args_handler, arg)
            if type(m) == types.MethodType:
                m()
