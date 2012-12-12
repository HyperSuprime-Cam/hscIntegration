from collections import OrderedDict


class Integration(object):
    """A suite of integration tests"""
    _known = OrderedDict() # List of known tests by name; to be executed in order

    def __init__(self, only=[], deactivate=[]):
        """Construct an integration test suite containing tests with the provided names"""
        self._tests = OrderedDict()
        deactivate = set(deactivate)
        for name, test in self._known.iteritems():
            if (len(only) == 0 or name in only) and deactivate.isdisjoint(test.keywords):
                self.addTest(self._known[name])

    def addTest(self, test):
        self._tests[test.name] = test

    def run(self, **kwargs):
        for test in self._tests.itervalues():
            success = test.run(**kwargs)
            print "Test %s: %s" % (test.name, "PASS" if success else "FAIL")

    @classmethod
    def register(cls, test):
        name = test.name
        if name in cls._known:
            raise RuntimeError("Test %s already exists" % name)
        cls._known[name] = test

    @classmethod
    def getTests(cls):
        return cls._known.keys()

    @classmethod
    def getKeywords(cls):
        keywords = set()
        for test in cls._known.values():
            keywords.update(test.keywords)
        return keywords
