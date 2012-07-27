import os
import sys
import time
import datetime
import subprocess, shlex

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
        self.log = open("%s.log" % self.name, "a")
        self.log.write("*** Test run starting at %s\n" % datetime.datetime.now())
        self.success = True

    def run(self, **kwargs):
        for method in ('preHook', 'execute', 'validate', 'postHook'):
            @guard
            def runMethod(self, **runKwargs):
                getattr(self, method)(**runKwargs)

            self.log.write("*** Running %s %s\n" % (self.name, method))
            runMethod(self, **kwargs)
            self.log.flush()
        return self.success

    def preHook(self, **kwargs):
        pass

    def execute(self, **kwargs):
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

    def validate(self, **kwargs):
        raise NotImplemented("Should be implemented by subclass")

    def postHook(self, **kwargs):
        pass


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

    def execute(self, workDir=".", **kwargs):
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
                self.log.write("*** Failed.\n")
                return

        if not self._call("eups list -s --nolocks", stdout=self.log):
            self.success = False
            self.log.write("*** Failed.\n")
            return
        self.commandList = substituteList(self.commandList, "@WORKDIR@", workDir)
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
        
    def execute(self, nodes=4, procs=8, **kwargs):
        self.commandList = substituteList(self.commandList, "@NODES@", str(nodes))
        self.commandList = substituteList(self.commandList, "@PROCS@", str(procs))
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
        lines = stream.strip().splitlines()
        if len(lines) != 1 or not lines[0][0].isdigit():
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

    @guard
    def validatePbs(self, *args, **kwargs):
        pbsLog = self.name + ".o" + self.job.partition('.')[0]
        self.assertTrue("PBS log file is " + pbsLog, os.path.isfile(pbsLog))

        bad = False
        for line in open(pbsLog):
            if line.startswith("=>> PBS: job killed") or \
               line.startswith("=   BAD TERMINATION OF ONE OF YOUR APPLICATION PROCESSES") or\
               line.startswith("Uncaught exception caused abortion") or \
               line.startswith("application called MPI_Abort"):
                bad = True
                break
        self.assertFalse("PBS log file clean of incompletion indicators", bad)


def substituteList(inList, old, new):
    """For each of the values in inList, replace 'old' with 'new', and descend recursively"""
    return [val.replace(old, new) if isinstance(val, basestring) else substituteList(val, old, new) for
            val in inList]
