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

ACTIONS = ('create', 'update')
BRANCHES = ('master', 'jethro', 'dizzy', 'daisy', 'noexists')
CATEGORIES = ('Full pass', 'Weekly')

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
        choices=ACTIONS,
        help='Action to execute can be create or update.')
    parser.add_argument('-p', '--product', required=False,
        dest="product_name", help='Product to create or update.')
    parser.add_argument('-c', '--category', required=False,
        choices=CATEGORIES,
        dest="category_name", help='Category for create or update.')
    parser.add_argument('-b', '--branch', required=False,
        choices=BRANCHES,
        dest="branch_name", help='Branch for create or update.')
    parser.add_argument('-e', '--environment', required=False,
        dest="env_name", help='Enviroment for create or update.')
    parser.add_argument('-o', '--optional', required=False,
        dest="optional", help='Optional parameter for get Test runs.')

    parser.add_argument('--project-version', required=False,
        dest="project_version", help='Version of the project.')
    parser.add_argument('--project-milestone', required=False,
        dest="project_milestone", help='Milestone of the project.')
    parser.add_argument('--project-revision', required=False,
        dest="project_revision", help='SCM Revision of the project.')
    parser.add_argument('--project-date', required=False,
        dest="project_date", help='SCM version/revision date of the project.')

    parser.add_argument('--results-log', required=False,
        dest="results_log", help='Results log.')

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
    testopia_opts = testopia_config + ['action', 'product_name', 'category_name',
        'project_version', 'project_milestone', 'project_revision',
        'project_date']
 
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

    params = ['action', 'product_name', 'branch_name', 'env_name']
    for p in params:
        if not getattr(args, p):
            logger.error("%s: Requires %s to be specified." % (sys.argv[0], p))
            sys.exit(1)

    product = get_product_class(args.product_name, products)
    if not product:
        logger.error("%s: Product %s isn't supported, use --list-products for "\
            "list available products." % \
            (sys.argv[0], args.product_name))
        sys.exit(1)

    test_plan = product.get_test_plan(args.branch_name)
    if not test_plan:
        logger.error("%s: Test plan for product %s and branch %s not exists."\
             % (sys.argv[0], args.product_name, args.branch_name))

        sys.exit(1)

    env = product.get_environment(test_plan, args.env_name)
    if not env:
        if args.action == "create":
            env = product.create_environment(test_plan, args.env_name)
            logger.info("%s: Create environment %s for product %s."\
                % (sys.argv[0], args.env_name, args.product_name))
        else:
            logger.error("%s: Product %s have invalid environment %s."\
                 % (sys.argv[0], args.product_name, args.env_name))
            logger.error("Available environments are:")
            for env_name in product.get_environment_names(test_plan):
                logger.error(env_name)
            sys.exit(1)

    build = product.get_build(test_plan, args.project_version,
        args.project_milestone, args.project_revision, args.project_date)
    if not build:
        if args.action == "create":
            build = product.create_build(test_plan, args.project_version,
                args.project_milestone, args.project_revision, args.project_date)
            logger.info("%s: Create build for product %s with: "\
                "%s, %s, %s, %s." % (sys.argv[0], args.product_name,
                args.project_version, args.project_milestone,
                args.project_revision, args.project_date))
        else:
            logger.error("%s: Product %s can't find build with: "\
                "%s, %s, %s, %s." % (sys.argv[0], args.product_name,
                args.project_version, args.project_milestone,
                args.project_revision, args.project_date))
            sys.exit(1)

    if args.action == "create":
        template_test_run = product.get_template_test_run(test_plan, args.project_version,
                args.category_name, args.optional)
        if not template_test_run:
            logger.error("%s: Product %s can't find test run with: "\
                "%s, %s, %s." % (sys.argv[0], args.product_name,
                args.project_version, args.category_name, args.optional))
            sys.exit(1)

        test_run = product.create_test_run(test_plan, env, build,
                template_test_run, args.project_version, args.project_date)
        if not test_run:
            logger.error("%s: Product %s can't create test run with: "\
                "%s, %s, %s, %s." % (sys.argv[0], args.product_name,
                args.project_version, args.project_date, args.category_name,
                args.optional))
            sys.exit(1)
        logger.info("%s: Test run was created with Template (%d), Summary (%s)"\
                " and ID (%s)." % (sys.argv[0], template_test_run['run_id'], 
                test_run['summary'], test_run['run_id']))
    elif args.action == "update":
        if not args.results_log:
            logger.error("%s: For update --results-log needs to be specified." \
                % (sys.argv[0]))
            sys.exit(1)
        if not os.path.exists(args.results_log):
            logger.error("%s: Results log (%s) don't exists." \
                % (sys.argv[0], args.results_log))
            sys.exit(1)

        results = product.parse_results_log(args.results_log)
        test_run = product.get_test_run(test_plan, env, build, args.project_date,
                args.project_version, args.category_name, args.optional)
        if not test_run:
            logger.error("%s: Product %s can't find test run with: "\
                "%s, %s, %s, %s." % (sys.argv[0], args.product_name,
                args.project_date, args.project_version, args.category_name,
                args.optional))
            sys.exit(1)

        missing = product.update_test_run(env, build, test_run, results)
        for tcid in missing:
            logger.warn("%s: Product %s, Test run %d, Case %d wasn't updated" %\
                    (sys.argv[0], args.product_name, test_run['run_id'], tcid))
    sys.exit(0)
