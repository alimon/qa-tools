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

    def get_environment(self, tp, env_name):
        tp_envs = self.testopia.product_get_environments(tp['product_id'])
        for tp_env in tp_envs:
            if env_name == tp_env['name']:
                return tp_env
        return None

    def create_environment(self, tp, env_name):
        return self.testopia.environment_create(tp['product_id'], True,
                name=env_name)

    def get_environment_names(self, tp):
        tp_envs = self.testopia.product_get_environments(tp['product_id'])
        return [tp_env['name'] for tp_env in tp_envs]

    def _format_build_name(self, project_version, project_revision):
        return "%s: %s" % (project_version, project_revision)

    def get_build(self, tp, project_version, project_milestone,
            project_revision, project_date):
        builds = self.testopia.product_get_builds(tp['product_id'])
        build_name = self._format_build_name(project_version, project_revision)
        for b in builds:
            if build_name == b['name'] and project_date == b['description'] \
                    and project_milestone == b['milestone']:
                return b
        return None

    def create_build(self, tp, project_version, project_milestone,
            project_revision, project_date):
        build_name = self._format_build_name(project_version, project_revision)

        return self.testopia.build_create(build_name, tp['product_id'],
                description=project_date, milestone=project_milestone,
                isactive=True)

    def _get_test_run_summary_alternatives(self, project_version,
            category_name, optional):
        summary_alts = []
        summary_alts.append('TEMPLATE - %s - %s - %s' % (self.name,
            project_version, category_name))
        summary_alts.append('TEMPLATE - %s - %s' % (project_version,
            category_name))
        summary_alts.append('TEMPLATE - %s' % (category_name))
        if optional: 
            for idx, sa in enumerate(summary_alts):
                summary_alts[idx] = sa + " - %s" % optional
        return summary_alts

    def get_template_test_run(self, tp, project_version, category_name,
            optional):
        """
            Discover the template for create the new test runs.

            First get summary alternative names and then search for the
            first match of summary in test runs.
        """

        summary_alts = self._get_test_run_summary_alternatives(project_version,
            category_name, optional)
        tp_test_runs = self.testopia.testplan_get_test_runs(tp['plan_id'])

        test_run = None
        for sa in summary_alts:
            for tr in tp_test_runs:
                if sa == tr['summary']:
                    test_run = tr
                    break

        return test_run

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
