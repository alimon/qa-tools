class Product(object):
    def __init__(self, testopia, opts, logger, config):
        self.testopia = testopia
        self.opts = opts
        self.logger = logger
        self.config = config

    def support(self, name):
        if self.name == name:
            return True
        return False

    def get_test_plan(self, branch_name):
        tp = None

        tp_name = '%s: %s branch' % (self.name, branch_name)

        tp = self.testopia.testplan_list(name=tp_name)
        if not tp:
            tp_alt_name = '%s: %s branch' % (self.name, branch_name.lower())
            tp = self.testopia.testplan_list(name=tp_alt_name)

        if tp:
            return tp[0]

        return tp


def get_products(testopia, opts, config, logger):
    from . import bsp_qemu

    products = []

    products.append(bsp_qemu.BSPQEMUProduct(testopia, opts, logger, config))

    return products

def get_product_class(product_name, products):
    for p in products:
        if p.name == product_name:
            return p

    return None
