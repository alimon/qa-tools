#!/usr/bin/env python

import os
import sys
import argparse
import logging
import ConfigParser
import types

from external.testopia import Testopia
from testopia_update.product import get_products, get_product_class

DEFAULT_CONFIG_FILE = "testopia_update.config"
DEFAULT_STORE_LOCATION = "/tmp/testopia_update"

class Options(object):
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

    parser.add_argument('-a', '--action', required=False, dest='action',
        choices=['create', 'update'],
        help='Action to execute can be create or update.')
    parser.add_argument('-p', '--product', required=False,
        dest="product_name", help='Product to create or update.')

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

    testopia_config = ['url', 'username', 'password', 'store_location']
    testopia_opts = testopia_config + ['action', 'product_name']
 
    config = None
    if not args.config and os.path.exists(DEFAULT_CONFIG_FILE):
        args.config = DEFAULT_CONFIG_FILE

    if args.config:
        config = ConfigParser.SafeConfigParser()
        config.read(args.config)

        for to in testopia_config:
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

    if not os.path.exists(opts.store_location):
        os.makedirs(opts.store_location)

    testopia = Testopia(opts.username, opts.password, opts.url, sslverify=False)
    products = get_products(testopia, opts, logger, config)

    if args.list_products:
        print("List of available products: \n")
        for p in products:
            print("%s\n" % p.name)
        sys.exit(0)

    if not (args.action and args.product_name):
        logger.error("%s: Requires action and product to be specified." % \
            (sys.argv[0]))
        sys.exit(1)

    product = get_product_class(args.product_name, products)
    if not product:
        logger.error("%s: Product %s isn't supported, use --list-products for "\
            "list available products." % \
            (sys.argv[0], args.product_name))
        sys.exit(1)
