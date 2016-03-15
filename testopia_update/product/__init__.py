import re

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
                    and project_milestone == str(b['milestone']):
                return b
        return None

    def create_build(self, tp, project_version, project_milestone,
            project_revision, project_date):
        build_name = self._format_build_name(project_version, project_revision)

        return self.testopia.build_create(build_name, tp['product_id'],
                description=project_date, milestone=project_milestone,
                isactive=True)

    def _get_test_run_summary_alternatives(self, ttype, project_version,
            category_name, optional):
        summary_alts = []
        summary_alts.append('%s - %s - %s - %s' % (ttype, self.name,
            project_version, category_name))
        summary_alts.append('%s - %s - %s' % (ttype, project_version,
            category_name))
        summary_alts.append('%s - %s' % (ttype, category_name))
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

        summary_alts = self._get_test_run_summary_alternatives("TEMPLATE", 
            project_version, category_name, optional)
        tp_test_runs = self.testopia.testplan_get_test_runs(tp['plan_id'])

        test_run = None
        for sa in summary_alts:
            for tr in tp_test_runs:
                if sa == tr['summary']:
                    test_run = tr
                    break

        return test_run

    def get_test_run(self, tp, env, build, project_date, project_version,
            category_name, optional):
        summary_alts = self._get_test_run_summary_alternatives(project_date, 
            project_version, category_name, optional)
        tp_test_runs = self.testopia.testplan_get_test_runs(tp['plan_id'])

        test_run = None
        for sa in summary_alts:
            for tr in tp_test_runs:
                if sa == tr['summary'] and build['build_id'] == tr['build_id'] \
                        and env['environment_id'] == tr['environment_id']:
                    test_run = tr
                    break

        return test_run

    def _get_test_case_ids(self, tr):
        return [tc['case_id'] for tc in \
                self.testopia.testrun_get_test_cases(tr['run_id'])]

    def _canonicalize_project_version(self, project_version):
        """
            Only conserve the version part of the Project remove Milestones.
        """

        regex = "^(?P<version>(\d+\.)?(\d+\.)?(\*|\d+)).*$"
        if hasattr(self, 'project_version_regex'):
            regex = getattr(self, 'project_version_regex')

        m = re.search(regex, project_version)
        if m:
            return m.group('version')

        return project_version

    def create_test_run(self, tp, env, build, template_tr, project_version, project_date):
        summary = template_tr['summary'].replace('TEMPLATE', project_date)

        test_case_ids = self._get_test_case_ids(template_tr)
        new_test_run = self.testopia.testrun_create(build['build_id'],
            env['environment_id'], tp['plan_id'], summary, self.testopia.userId,
            product_version=self._canonicalize_project_version(project_version))
        self.testopia.testrun_add_cases(test_case_ids, new_test_run['run_id'])

        return new_test_run

    def parse_results_log(self, log_file):
        regex = "^.*RESULTS.*(?P<case_id>\d+): (?P<status>PASSED|FAILED)$"
        if hasattr(self, 'results_regex'):
            regex = getattr(self, 'results_regex')

        regex_comp = re.compile(regex)

        results = {}
        with open(log_file, "r") as f:
            for line in f:
                m = regex_comp.search(line)
                if m:
                    results[int(m.group('case_id'))] = m.group('status')

        return results


def get_products(testopia, opts, config, logger):
    from . import bsp_qemu
    from . import toaster

    products = []

    products.append(bsp_qemu.BSPQEMUProduct(testopia, opts, logger, config))
    products.append(toaster.ToasterProduct(testopia, opts, logger, config))

    return products

def get_product_class(product_name, products):
    for p in products:
        if p.name == product_name:
            return p

    return None
