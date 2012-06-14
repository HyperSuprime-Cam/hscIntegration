import os
import subprocess, shlex

import hsc.pipe.base.camera as hscCamera
import lsst.meas.astrom.astrom as measAstrom


class Integrator(object):
    def __init__(self, tests=[]):
        self._tests = tests

    def addTest(self, test):
        self._tests.append(test)

    def run(self):
        for test in self._tests:
            success = test.run()
            print "Test %s: %s" % (test.name, "PASS" if success else "FAIL")



class Test(object):
    def __init__(self, name):
        self.name = name
        self.log = open("%s.log" % self.name, "w")
        self.success = True

    def run(self):
        try:
            success = self.execute() and self.validate()
        except Exception, e:
            self.log.write("*** Caught exception %s: %s\n" % (e.__class__, e))
            success = False
        return success and self.success

    def execute(self):
        raise NotImplemented("Should be implemented by subclass")

    def assertTrue(self, description, success):
        self.log.write("*** %s: %s\n" % (description, "PASS" if success else "FAIL"))
        self.success = self.success and success

    def assertFalse(self, description, success):
        self.assertTrue(description, not success)

    def assertGreater(self, description, num1, num2):
        self.assertTrue(description + " (%d > %d)" % (num1, num2), num1 > num2)

    def assertLess(self, description, num1, num2):
        self.assertTrue(description + " (%d < %d)" % (num1, num2), num1 < num2)

    def assertGreaterEqual(self, description, num1, num2):
        self.assertTrue(description + " (%d >= %d)" % (num1, num2), num1 >= num2)

    def assertLessEqual(self, description, num1, num2):
        self.assertTrue(description + " (%d <= %d)" % (num1, num2), num1 <= num2)

    def validate(self):
        raise NotImplemented("Should be implemented by subclass")



class CommandTest(Test):
    def __init__(self, name, command, setups=[]):
        super(CommandTest, self).__init__(name)
        self.command = command
        self.setups=[]

    def execute(self):
        class Logger(object):
            def __init__(self, log):
                self.log = log
                self.stream = ""
            def write(self, s):
                self.log.write(s)
                self.log.flush()
                self.stream += s
            def fileno(self):
                return self.log.fileno()

        logger = Logger(self.log)

        def call(command):
            logger.write("*** Executing: %s\n" % command)
            ret = subprocess.call(shlex.split(command), stdout=logger, stderr=subprocess.STDOUT)
            logger.write("*** Return code: %d\n" % ret)
            return ret

        for setup in self.setups:
            call("setup -j %s" % setup)
            
        call("eups list -s")
        ret = call(self.command)
        self.stream = logger.stream # In case we want to grep the logs for validation
        return ret == 0


class ProcessCcdTest(CommandTest):
    def __init__(self, name, camera, visit, ccd, dir=None, rerun=None, minMatches=30, minSources=2000,
                 datasets=["icSrc", "icMatch", "src", "calexp"]

                 ):
        self.camera = camera
        self.visit = visit
        self.ccd = ccd
        self.dataId = {'visit': visit, 'ccd': ccd}
        self.dir = dir if dir is not None else os.environ['HSCINTEGRATIONDATA_DIR']
        self.rerun = rerun
        self.minMatches = minMatches
        self.minSources = minSources
        self.datasets = set(datasets)

        command = os.path.join(os.environ['HSCPIPE_DIR'], 'bin', 'scProcessCcd.py') + \
                  " " + camera + " " + self.dir + " --doraise --id visit=%d ccd=%d" % (self.visit, self.ccd)
        
        super(ProcessCcdTest, self).__init__(name, command)
        

    def validate(self):
        butler = hscCamera.getButler(self.camera, rerun=self.rerun)

        for ds in self.datasets:
            self.assertTrue("%s exists" % ds, butler.datasetExists(datasetType=ds, dataId=self.dataId))
            data = butler.get(ds, self.dataId)
            if hasattr(data, '__subject__'):
                # Foil read proxy
                data = data.__subject__
            self.assertTrue("%s readable" % ds, data)

        src = butler.get('src', self.dataId)
        self.assertGreater("Number of sources", len(src), self.minSources)

        matches = measAstrom.readMatches(butler, self.dataId)
        self.assertGreater("Number of matches", len(matches), self.minMatches)

        return self.success
