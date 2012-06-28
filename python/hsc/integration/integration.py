import os
import sys
import re
import time
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


def guard(method):
    """Decorator to guard a method against exceptions"""
    def guarded(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception, e:
            self.log.write("*** Caught exception %s: %s\n" % (e.__class__, e))
            self.success = False
    return guarded


class Test(object):
    def __init__(self, name):
        self.name = name
        self.log = open("%s.log" % self.name, "w")
        self.success = True

    def run(self):
        try:
            if self.success:
                self.execute()
            if self.success:
                self.validate()
        except Exception, e:
            self.log.write("*** Caught exception %s: %s\n" % (e.__class__, e))
            self.success = False
        return self.success

    def execute(self):
        raise NotImplemented("Should be implemented by subclass")

    def assertTrue(self, description, success):
        self.log.write("*** %s: %s\n" % (description, "PASS" if success else "FAIL"))
        self.success = self.success and success

    def assertFalse(self, description, success):
        self.assertTrue(description, not success)

    @guard
    def assertEqual(self, description, obj1, obj2):
        self.assertTrue(description + " (%s = %s)" % (obj1, obj2), obj1 == obj2)

    @guard
    def assertGreater(self, description, num1, num2):
        self.assertTrue(description + " (%d > %d)" % (num1, num2), num1 > num2)

    @guard
    def assertLess(self, description, num1, num2):
        self.assertTrue(description + " (%d < %d)" % (num1, num2), num1 < num2)

    @guard
    def assertGreaterEqual(self, description, num1, num2):
        self.assertTrue(description + " (%d >= %d)" % (num1, num2), num1 >= num2)

    @guard
    def assertLessEqual(self, description, num1, num2):
        self.assertTrue(description + " (%d <= %d)" % (num1, num2), num1 <= num2)

    def validate(self):
        raise NotImplemented("Should be implemented by subclass")



class CommandsTest(Test):
    def __init__(self, name, commandList, setups=[], **kwargs):
        super(CommandsTest, self).__init__(name, **kwargs)
        self.commandList = commandList
        self.setups=[]
        self.stream = None

    def _call(self, command, stdout=sys.stdout):
        """Execute a command, returning success rather than exit code"""
        self.log.write("*** Executing: %s\n" % command)
        if isinstance(command, basestring):
            command = shlex.split(command)

        # We would use subprocess.call() except that doesn't allow us to capture output (it wants to write to
        # a file descriptor, even if given a file, so we can't use our Logger to capture the stream).
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out,err = proc.communicate()
        stdout.write(out)
        ret = proc.returncode

        self.log.write("*** Return code: %d\n" % ret)
        return ret == 0

    def execute(self):
        class Logger(object):
            """A replacement for stdout that writes to our log file as well as saving the stream as a string"""
            def __init__(self, logFile):
                self.log = logFile
                self.stream = ""
            def write(self, s):
                self.log.write(s)
                self.log.flush()
                self.stream += s

        logger = Logger(self.log)

        for setup in self.setups:
            if not self._call("setup -j %s" % setup, stdout=self.log):
                self.success = False
                self.log.write("*** Failed.")
                return

        if not self._call("eups list -s", stdout=self.log):
            self.success = False
            self.log.write("*** Failed.")
            return
        for command in self.commandList:
            if not self._call(command, stdout=logger):
                self.success = False
                self.log.write("*** Failed.")
                break
        self.stream = logger.stream # In case we want to grep the logs for validation


class PbsTest(CommandsTest):
    """Test a command that submits a job to PBS.

    This assumes that the command to be run produces a single line of output containing solely the PBS job
    identifier.  If this is not the case, override the getIdentifier() method.

    By default, the execution blocks until the job is done.  This is not the most efficient way to do multiple
    tests, but it's easy and involves the least modification to the integrator.  This behaviour can be
    disabled by setting wait=False in the constructor.

    The SLEEP class variable controls the length of time between qstat polls.
    """
    
    SLEEP = 30 # Number of seconds to sleep between polling qstat

    def __init__(self, name, commandList, setups=[], wait=True):
        super(PbsTest, self).__init__(name, commandList, setups=setups)
        self.wait = wait
        
    def execute(self):
        super(PbsTest, self).execute()
        self.job = self.getIdentifier(self.stream)
        print "Test %s: waiting for PBS job %s" % (self.name, self.job)
        if self.job is None:
            self.success = False
            return False
        if self.wait and self.success:
            self._wait()
        
    def getIdentifier(self, stream):
        """Get the PBS job identifier from the provided stream string"""
        lines = re.split("\n", stream.strip())
        if len(lines) != 1 or not re.search("^\d+", lines[0]):
            self.log.write("*** ERROR: Expected only a single output line, containing the PBS job identifier")
            return None
        return lines[0]

    def _wait(self):
        """Block until the job is done"""
        while True:
            if not self._call("qstat " + self.job, stdout=self.log):
                # Can't find job, so we must be done
                return
            time.sleep(self.SLEEP)
