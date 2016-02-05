import unittest, time, re, sys, getopt, os, logging, string, errno, exceptions
import shutil, argparse, ConfigParser, platform
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

class InitToaster(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.timeout = 320

    def is_text_present (self, patterns):
        for pattern in patterns:
            if str(pattern) not in self.driver.page_source:
                print pattern
                return False
        return True

    def test_setupToaster(self):
        self.driver.maximize_window()
        self.driver.get("localhost:8000")
        try:
            self.driver.find_element_by_css_selector("a[href='/toastergui/projects/']").click()
        except:
            self.driver.find_element_by_id("new-project-button").click()
            self.driver.find_element_by_id("new-project-name").send_keys("selenium-project")
            self.driver.find_element_by_id("create-project-button").click()
        try:
            self.driver.find_element_by_link_text("selenium-project").click()
        except:
            self.driver.find_element_by_id("new-project-button").click()
            self.driver.find_element_by_id("new-project-name").send_keys("selenium-project")
            self.driver.find_element_by_id("create-project-button").click()
        time.sleep(5)
        #workaround
#        self.driver.find_element_by_partial_link_text("Bitbake").click()
#        self.driver.find_element_by_id("config_var_trash_10").click()
#        time.sleep(5)
        #queue up a core-image-minimal
        self.driver.find_element_by_id("build-input").send_keys("core-image-minimal")
        self.driver.find_element_by_id("build-button").click()
        time.sleep(20)
        #queue up a core-image-sato
        self.driver.find_element_by_id("build-input").send_keys("core-image-sato")
        self.driver.find_element_by_id("build-button").click()
        time.sleep(20)
        #go back to the main project page
        self.driver.find_element_by_css_selector("a[href='/toastergui/projects/']").click()
        self.driver.find_element_by_link_text("selenium-project").click()
        #check if meta-selftest layer is added and import it if it's not
        if not (self.is_text_present("meta-selftest")):
            self.driver.find_element_by_css_selector("a[href='/toastergui/project/2/importlayer']").click()
            self.driver.find_element_by_id("import-layer-name").send_keys("meta-selftest")
            self.driver.find_element_by_id("layer-git-repo-url").send_keys("git://git.yoctoproject.org/poky")
            self.driver.find_element_by_id("layer-subdir").send_keys("meta-selftest")
            self.driver.find_element_by_id("layer-git-ref").send_keys("HEAD")
            self.driver.find_element_by_id("import-and-add-btn").click()
        #queue up an error-image build
        self.driver.find_element_by_id("build-input").send_keys("error-image")
        self.driver.find_element_by_id("build-button").click()
        time.sleep(5)
        #move to all builds page
        self.driver.find_element_by_css_selector("a[href='/toastergui/builds/']").click()
        time.sleep(5)
        self.driver.refresh()
        #check progress bar is displayed to signal a build has started
        try:
            self.driver.find_element_by_xpath("//div[@class='progress']").is_displayed()
        except:
            print "Unable to start new build"
            self.fail(msg="Unable to start new build")
        count = 0
        failflag = False
        try:
            self.driver.refresh()
            time.sleep(1)
            print "First check starting"
            while (self.driver.find_element_by_xpath("//div[@class='progress']").is_displayed()):
                #print "Looking for build in progress"
                print 'Builds running for '+str(count)+' minutes'
                count += 5
                #timeout default is at 179 minutes(3 hours); see set_up method to change
                if (count > self.timeout):
                    failflag = True
                    print 'Builds took longer than expected to complete; Failing due to possible build stuck.'
                    self.fail()
                time.sleep(300)
                self.driver.refresh()
        except:
           try:
                if failflag:
                    self.fail(msg="Builds took longer than expected to complete; Failing due to possible build stuck.")
                print "Looking for successful build"
                self.driver.find_element_by_xpath("//div[@class='alert build-result alert-success']").is_displayed()
           except:
                if failflag:
                    self.fail(msg="Builds took longer than expected to complete; Failing due to possible build stuck.")
                print 'Builds did not complete successfully'
                self.fail(msg="Builds did not complete successfully.")
        print "Builds complete!"

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
