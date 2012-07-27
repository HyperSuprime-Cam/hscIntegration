from collections import OrderedDict


class Integration(object):
    """A suite of integration tests"""
    _known = OrderedDict()

    def __init__(self, exclude=[]):
        """Construct an integration test suite containing tests with the provided names"""
        self._tests = OrderedDict()
        for name in self._known:
            if name not in exclude:
                self.addTest(self._known[name])

    def addTest(self, test):
        self._tests[test.name] = test

    def run(self, **kwargs):
        for test in self._tests.itervalues():
            success = test.run(**kwargs)
            print "Test %s: %s" % (test.name, "PASS" if success else "FAIL")

    @classmethod
    def register(cls, test):
        cls._known[test.name] = test

    @classmethod
    def getTests(cls):
        return cls._known.keys()
