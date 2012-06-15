import os
import subprocess, shlex


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

    def assertEqual(self, description, obj1, obj2):
        self.assertTrue(description + " (%s = %s)" % (obj1, obj2), obj1 == obj2)

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



class CommandsTest(Test):
    def __init__(self, name, commandList, setups=[]):
        super(CommandsTest, self).__init__(name)
        self.commandList = commandList
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

        success = True
        def call(command):
            logger.write("*** Executing: %s\n" % command)
            if isinstance(command, basestring):
                command = shlex.split(command)
            ret = subprocess.call(command, stdout=logger, stderr=subprocess.STDOUT)
            logger.write("*** Return code: %d\n" % ret)
            success = self.success and ret == 0

        for setup in self.setups:
            call("setup -j %s" % setup)

        call("eups list -s")
        for command in self.commandList:
            call(command)
        self.stream = logger.stream # In case we want to grep the logs for validation
        self.success = self.success and success
        return success
