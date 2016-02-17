#!/usr/bin/env python

import sys
import os
import time
import re
from time import gmtime, strftime
import datetime
from external.testopia import Testopia
from difflib import SequenceMatcher as SM

def print_lava(string):
    os.system('echo '+string)

product_list = {'BSP/QEMU':['GenericX86-64', 'GenericX86-64-lsb', 'GenericX86-lsb','GenericX86', 'qemux86', 'qemux86_64','qemuarm','qemumips','qemuppc'],
                #'Hob':['Hob'],
                'BitBake':['BitBake'],
                'OE-Core':['OE-Core'],
                'Eclipse Plugin':['Kepler', 'Luna', 'Mars'],
                'Runtime':['Runtime'],
                'Toaster':['Backend', 'UI'],
                'Automated Build Testing':['Ubuntu','OpenSUSE','Fedora','CentOS']
                }

weekly_product_list = {'BSP/QEMU':['GenericX86-64', 'GenericX86', 'qemux86', 'qemux86_64','qemuarm','qemumips','qemuppc']}

#georgex.l.musat@intel.com 802
#costin.c.constantin@intel.com 925
#stanciux.mihail@intel.com 948
#alexandru.c.georgescu@intel.com 296
#cristina-danielax.agurida@intel.com 1228
#yi.zhao@windriver.com 96

product_owners = {'GenericX86-64':'802',
                'GenericX86-64-lsb':'802',
                'GenericX86-lsb':'802',
                'GenericX86':'802',
                'qemux86':'948',
                'qemux86_64':'948',
                'qemuarm':'96',
                'qemumips':'96',
                'qemuppc':'96',
                'Hob':'1228',
                'BitBake':'802',
                'Runtime':'802',
                'OE-Core':'925',
                'Kepler':'948',
                'Luna':'948',
                'Mars':'948',
                'Backend':'948',
                "UI":"948",
                'Ubuntu':'948',
                'OpenSUSE':'948',
                'Fedora':'948',
                'CentOS':'948'
}

product_environments = {'GenericX86-64':'genericx86-64 on NUC',
                'GenericX86-64-lsb':'genericx86-64 on NUC',
                'GenericX86-lsb':'genericx86 - on MMAX32bit',
                'GenericX86':'genericx86 - on MMAX32bit',
                'qemux86':'qemu-x86',
                'qemux86_64':'qemux86-64',
                'qemuarm':'qemuarm',
                'qemumips':'qemumips',
                'qemuppc':'qemuppc',
                'Hob':'Ubuntu 15.04 x86_64',
                'BitBake':'Ubuntu 15.04 x86_64',
                'Runtime':'Multiple Environments',
                'OE-Core':'Ubuntu 15.04 x86_64',
                'Kepler':'Ubuntu 15.04 x86_64',
                'Luna':'Ubuntu 15.04 x86_64',
                'Mars':'Ubuntu 15.04 x86_64',
                'Toaster Backend':'Ubuntu 15.04 x86_64',
                'Toaster UI':'Ubuntu 15.04 x86_64',
                'Ubuntu':'Ubuntu 15.04 x86_64',
                'OpenSUSE':'OpenSuse 13.2 x86_64',
                'Fedora':'Fedora 22 x86-64',
                'CentOS':'CentOS 7 x86_64'
}

branches = ["master","fido","dizzy","daisy"]

class YpTestopia(Testopia):

    def __init__(self, action, product, targets, branch, poky_version, poky_commit, fp_date, env, cloneweekly):
        env_id = None
        build_id = None
        yp_ver = poky_version.split('_')[0]
        yp_ver = yp_ver.replace('yocto-','')
        if (len(yp_ver) > 3):
            yp_ver = yp_ver[:3]
        poky_version = poky_version.replace('yocto-','')
        print("Getting product id for product %s and branch %s" % (product, branch))
        product_id = self.get_product_id(product, branch)

        self.product_id = product_id
        plan_id = self.get_plan_id(product, branch)
        try:
            env = product_environments[targets]
        except:
            pass
        env_id = self.get_env_id(product_id, env)
        build_id = self.get_build_id(product_id, poky_version, poky_commit, fp_date)

        if action == "create":
            self.create_testruns(targets, product_id, plan_id, build_id, env_id, fp_date, yp_ver, cloneweekly)
        elif action == "update":
            self.update_testrun(targets, plan_id, build_id, env_id, fp_date, yp_ver)
        print("Here4")

    def create_testruns(self, targets, product_id, plan_id, build_id, env_id, fp_date, yp_ver, cloneweekly):
        if cloneweekly:
            print "Should clone just the weekly runs!"
        else:
            print "Should clone all"
        if not env_id:
            t.environment_create(product_id, True, name=env)
            env_id = self.get_env_id(product_id, env)

        if not build_id:
            build_name = poky_version+': '+poky_commit
            try:
                build_milestone = poky_version.split('_')[0]+' '+poky_version.split('_')[1].split('.')[0]
                if len(str(poky_version.split('_')[0])) == 5:
                    build_milestone = poky_version.split('_')[0] #for point releases
            except:
                pv = re.search("([0-9]\.[0-9])", poky_version)
                if pv:
                    build_milestone = str(pv.group())
                else:
                    build_milestone = "1.1"
            t.build_create(build_name, product_id, fp_date, build_milestone, True)
            build_id =  self.get_build_id(product_id, poky_version, poky_commit, fp_date)

        orig_target = str(targets.split(' ')[0]).strip()
        if ("Generic" in targets):
            targets += " BSP"
        if ("lsb" in targets.lower()):
            targets = "LSB"
        if ("qemu" in targets):
            targets = "ANYQEMU"        

        print("Targets: "+str(targets))
        for target in targets.split(' '):
            print("Target: "+str(target))
            target = str(target).strip()
            if cloneweekly:
                summary = '^TEMPLATE - '+yp_ver+'.*'+target+' .*- Weekly.*'
            else:
                summary = '^TEMPLATE - '+yp_ver+'.*'+target+' .*- [Weekly|Full Pass].*'

            if ("Kepler" in targets) or ("Luna" in targets) or ("Mars" in targets):
                summary = '^TEMPLATE - '+yp_ver+'.*Eclipse .*- [Weekly|Full Pass].*'

            if ("Ubuntu" in targets) or ("OpenSUSE" in targets) or ("Fedora" in targets) or ("CentOS" in targets):
                summary = '^TEMPLATE - '+yp_ver+' - DISTRO'

            tmpl_run_ids = self.get_run_ids(plan_id, summary, build_id = None, env_id = None)
            if (tmpl_run_ids == []):
                print("No template found!")
            else:
                print "Templates found: "+str(tmpl_run_ids)
                for tmpl_run_id in tmpl_run_ids:
                    if not tmpl_run_id:
                        print_lava("Error: Couldn't find the test run template with id: "+str(tmpl_run_id)+" in the product test plan.")
                        if (product != "all"):
                            break
                    tmpl_summary = self.get_tr_attr(tmpl_run_id, 'summary')
                    summary = tmpl_summary.replace('TEMPLATE', fp_date)
                    summary = summary.replace(target, orig_target)
                    if ("_64" not in orig_target):
                        summary = summary.replace("_64", "")
                    try:
                        if (target == str(targets.split(' ')[1]).strip()):
                            summary = summary.replace('(Intel)', '') # ugly replace for legacy purposes                        
                    except:
                        pass

                    summary = summary.replace('Eclipse', str(target))
                    summary = summary.replace('DISTRO', 'DISTRO - '+str(target))

                    check_run_id = self.get_run_ids(plan_id, summary, build_id, env_id)
                    if not check_run_id:                        
                        new_run_id = t.testrun_create(build_id, env_id, plan_id, summary, t.userId, product_version=yp_ver)['run_id']
                        cases_list = self.tr_get_cases(tmpl_run_id)
                        t.testrun_add_cases(cases_list, new_run_id)
                        print_lava("Setting testrun to right owner...")
                        try:
                            t.testrun_update(run_id = new_run_id, status_id = 1, manager_id=int(product_owners[orig_target]))
                        except:
                            pass
                        try:
                            print_lava("----------")
                            print_lava("Test run "+str(new_run_id)+" was created and populated with test cases: "+str(cases_list))
                            print_lava("Test run template used was: "+str(tmpl_run_id))
                            print_lava("----------")
                        except:
                            pass
                        # Create an extra Weekly for Genericx86-64 on Minnowmax
                        if ('GenericX86-64' in str(targets)) and ('BSP' in str(target)) and not cloneweekly:
                            print("Creating extra weekly testrun...")
                            new_run_id = t.testrun_create(build_id, 172, plan_id, summary, t.userId, product_version=yp_ver)['run_id']
                            cases_list = self.tr_get_cases(tmpl_run_id)
                            t.testrun_add_cases(cases_list, new_run_id)
                            print_lava("Setting testrun to right owner...")
                            try:
                                t.testrun_update(run_id = new_run_id, status_id = 1, manager_id=int(product_owners[orig_target]))
                            except:
                                pass
                            try:
                                print_lava("----------")
                                print_lava("Test run "+str(new_run_id)+" was created and populated with test cases: "+str(cases_list))
                                print_lava("Test run template used was: "+str(tmpl_run_id))
                                print_lava("----------")
                            except:
                                pass
                            print("Creating extra WIC testrun...")
                            summary = summary.replace('GenericX86-64', 'GenericX86-64-WIC')
                            new_run_id = t.testrun_create(build_id, env_id, plan_id, summary, t.userId, product_version=yp_ver)['run_id']
                            cases_list = self.tr_get_cases(tmpl_run_id)
                            t.testrun_add_cases(cases_list, new_run_id)
                            print_lava("Setting testrun to right owner...")
                            try:
                                t.testrun_update(run_id = new_run_id, status_id = 1, manager_id=int(product_owners[orig_target]))
                            except:
                                pass
                            try:
                                print_lava("----------")
                                print_lava("Test run "+str(new_run_id)+" was created and populated with test cases: "+str(cases_list))
                                print_lava("Test run template used was: "+str(tmpl_run_id))
                                print_lava("----------")
                            except:
                                pass
                    else:
                        print_lava("Error: A test run with id: "+str(check_run_id)+" already exists.")

    ### update-ul de tr se va face dupa identificarea de tr dupa data - yp version - target - weekly
    def update_testrun(self, target, plan_id, build_id, env_id, fp_date, yp_ver):
        found = False
        for i in product_list:
            for product in product_list[i]:
                if target == product:
                    found = True
                    break
        #fuzzy match the target
        if not found:
            baseline = 0.75
            for i in product_list:
                for j in product_list[i]:
                    if SM(None, str(j), target).ratio() > baseline:
                        target = str(j)
                        baseline = SM(None, str(j), target).ratio()
        print_lava("Product found:")
        print_lava(target)
        env = product_environments[target]
        print "env:"+env
        print "product_id:"+str(self.product_id)
        env_id = self.get_env_id(self.product_id, env)
        print_lava("Environment id found:")
        print_lava(str(env_id))
        summary = '^'+fp_date+'.*'+target+' - Weekly.*'
        run_id = self.find_run_ids(plan_id, target, summary, build_id, env_id)[0]
        cases_list = self.tr_get_cases(run_id)
        cases_not_updated = []
        for case_id in cases_list:
            case_result = self.get_case_result(str(case_id))
            if not case_result:
                cases_not_updated.append(case_id)
            elif "PASS" in case_result:
                try:
                    t.testcaserun_update(run_id, case_id, build_id, env_id, case_run_status_id=2)
                except:
                    pass
            elif "FAIL" in case_result:
                try:
                    t.testcaserun_update(run_id, case_id, build_id, env_id, case_run_status_id=3)
                except:
                    pass
        print_lava("For test run "+str(run_id)+" the following test cases were not updated: "+str(cases_not_updated))

    def get_case_result(self, case, logfile='results.log'):
        selftest_log = open(logfile,'r')
        FILE = selftest_log.readlines()
        for line in FILE:
            if ("RESULTS" in line) and (case+":" in line):
                return str(line.split(': ')[1]).strip()

    def get_product_id(self, product, branch):
        try:
            tp = t.testplan_list(name=product+': '+branch+' branch')
        except Exception, e:
            print Exception, e
        if tp != []:
            product_id = tp[0]['product_id']
            return product_id
        else:
            tp = t.testplan_list(name=product+': '+str(branch).lower()+' branch')
            if tp != []:
                product_id = tp[0]['product_id']
                return product_id
            else:
                print "Cannot find product!"
                exit(1)

    def get_plan_id(self, product, branch):
        tp = t.testplan_list(name=product+': '+branch+' branch')
        plan_id = tp[0]['plan_id']
        return plan_id

    def get_env_id(self, product_id, env):
        tp_envs = t.product_get_environments(product_id)
        for envs in tp_envs:
            #print "Envs: "+str(envs)
            if env == str(envs['name']):
                return envs['environment_id']

    def get_build_id(self, product_id, poky_version, poky_commit, fp_date):
        tp_builds = t.product_get_builds(product_id)
        found = 0
        for build in tp_builds:
            if ((poky_version+": "+poky_commit == str(build['name'])) and (fp_date == str(build['description']))):
                found = 1
                return build['build_id']
        if (found == 0):
            print_lava("Cannot find the build id. Trying to find the closest match...")
            baseline = 0.75
            guess = ""
            for build in tp_builds:
                if SM(None, poky_version+": "+poky_commit, str(build['name'])).ratio() > baseline:
                    guess = build['build_id']
                    baseline = SM(None, poky_version+": "+poky_commit, str(build['name'])).ratio()
                    found = 1
            if (found == 1):
                print_lava("A close match found:")
                print_lava(str(guess))
                return guess
            else:
                print_lava("Cannot find a close match!")

    def get_tr_attr(self, run_id, attr):
        attr_info = t.testrun_get(run_id)[attr]
        return attr_info

    def get_run_ids(self, plan_id, summary, build_id, env_id):
        print("Searching for regex: "+summary)
        plan = t.testplan_get_test_runs(plan_id)
        run_ids = []
        if (not build_id and not env_id):
            for run in plan:
                if re.match(r''+summary+'', run['summary']):
                    run_ids.append(run['run_id'])
        else:
            for run in plan:
                if (re.match(r''+summary+'', run['summary']) and (build_id == run['build_id']) and (env_id == run['environment_id'])):
                    run_ids.append(run['run_id'])
        return run_ids

    def get_product_from_target(self, target):
        for i in product_list:
            for j in product_list[i]:
                if target == j:
                    return i

    def find_run_ids(self, plan_id, product, summary, build_id, env_id):
        print("Searching for regex: "+summary)        
        plan = t.testplan_get_test_runs(plan_id)
        run_ids = []
        if (not build_id and not env_id):
            for run in plan:
                if re.match(r''+summary+'', run['summary']):
                    run_ids.append(run['run_id'])
        else:
            for run in plan:
                if (re.match(r''+summary+'', run['summary']) and (build_id == run['build_id']) and (env_id == run['environment_id'])):
                    run_ids.append(run['run_id'])
        if not run_ids:
            print "Cannot detect runs in provided branch. Looking in the others..."
            run_ids = []
            for branch in branches:
                plan = t.testplan_get_test_runs(self.get_plan_id(self.get_product_from_target(product),branch))
                if (not build_id and not env_id):
                    for run in plan:
                        if re.match(r''+summary+'', run['summary']):
                            run_ids.append(run['run_id'])
                else:
                    for run in plan:
                        if (re.match(r''+summary+'', run['summary']) and (build_id == run['build_id']) and (env_id == run['environment_id'])):
                            run_ids.append(run['run_id'])
        return run_ids

    def tr_get_cases(self, run_id):
        cases_list = []
        for case in t.testrun_get_test_cases(run_id):
            cases_list.append(case['case_id'])
        return cases_list

try:
    action = str(sys.argv[1]).strip()
    product = str(sys.argv[2]).strip()
    targets = str(sys.argv[3]).strip()
    branch = str(sys.argv[4]).strip()
    poky_version = str(sys.argv[5]).strip()
    poky_commit = str(sys.argv[6]).strip()
    fp_date = str(sys.argv[7]).strip()
    env = str(sys.argv[8]).strip()
except IndexError, NameError:
    print "Usage: ./update_testopia.py <action_type> <product> <target(s)> <branch> <poky_version> <poky_commit> <date> <environment>"
    print "Example: ./update_testopia.py create BSP/QEMU GenericX86-64 master 1.8_M2.RC1 bf3b0601fa45b98ad33a2e4fd048f3616f50d8da 2015-02-02 'Ubuntu 14.10 x86_64'"
    print "Example: ./update_testopia.py create BSP/QEMU all master 1.8_M2.RC1 bf3b0601fa45b98ad33a2e4fd048f3616f50d8da 2015-02-02 'Ubuntu 14.10 x86_64'"
    print "Example: ./update_testopia.py create all all master 1.8_M2.RC1 bf3b0601fa45b98ad33a2e4fd048f3616f50d8da 2015-02-02 'Ubuntu 14.10 x86_64'"
    print "Example: ./update_testopia.py update OE-Core OE-Core master 1.8_M2.RC1 bf3b0601fa45b98ad33a2e4fd048f3616f50d8da 2015-02-02 'Ubuntu 14.10 x86_64'"    
    print "Templates must exist using format [TEMPLATE - ver - machine - Weekly -...] [TEMPLATE - ver - machine - Full Pass -...]"
    exit(1)

#Try to fix bad branch parameter
if ('1.6' in poky_version) and (branch != 'daisy'):
    branch = 'daisy'
    print_lava("Branch and version mismatch. Setting branch as daisy.")
elif ('1.7' in poky_version) and (branch != 'dizzy'):
    branch = 'dizzy'
    print_lava("Branch and version mismatch. Setting branch as dizzy.")
elif ('1.8' in poky_version) and (branch != 'fido'):
    branch = 'fido'
    print_lava("Branch and version mismatch. Setting branch as fido.")
elif ('1.9' in poky_version) and (branch != 'master'):
    branch = 'master'
    print_lava("Branch and version mismatch. Setting branch as master.")
elif ('2.0' in poky_version) and (branch != 'master'):
    branch = 'master'
    print_lava("Branch and version mismatch. Setting branch as master.")


t = Testopia('ionutx.chisanovici@intel.com', 'thefatlady', 'https://bugzilla.yoctoproject.org/xmlrpc.cgi')
#t = Testopia('ionutx.chisanovici@intel.com', 'thefatlady', 'https://bugzilla.ctest.yoctodev.org/xmlrpc.cgi')
if (product == "all"):
    if (targets == "weekly"):
        product_list = weekly_product_list
    for product in product_list:
        for i in product_list[product]:
            print "Running: YpTestopia("+action+", "+product+", "+i+", "+branch+", "+poky_version+", "+poky_commit+", "+fp_date+", '"+env+"')"
            env = "'"+env.replace("'","")+"'"
            try:
                YpTestopia(action, product, i, branch, poky_version, poky_commit, fp_date, env, cloneweekly=False)
            except:
                pass
elif (product == "getid"):
    print t.user_lookup_id_by_login(targets)
elif (targets == "all") and (product != "all"):
    for i in product_list[product]:
        print "Running: YpTestopia("+action+", "+product+", "+i+", "+branch+", "+poky_version+", "+poky_commit+", "+fp_date+", '"+env+"')"
        env = "'"+env.replace("'","")+"'"
        try:
            YpTestopia(action, product, i, branch, poky_version, poky_commit, fp_date, env, cloneweekly=False)
        except:
            pass
else:
    try:
        YpTestopia(action, product, targets, branch, poky_version, poky_commit, fp_date, env, cloneweekly=False)
    except:
        pass
