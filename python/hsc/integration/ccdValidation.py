from hsc.integration.test import Test, guard
import lsst.meas.astrom.astrom as measAstrom


class CcdValidationTest(Test):
    """Mix-in class to validate a CCD"""
    def __init__(self, name, minMatches=10, minSources=100,
                 datasets=["icSrc", "icMatch", "psf", "apCorr", "src", "calexp"],
                 **kwargs):
        super(CcdValidationTest, self).__init__(name, **kwargs)
        self.minMatches = minMatches
        self.minSources = minSources
        self.datasets = set(datasets)

    @guard
    def validateDataset(self, butler, dataId, dataset):
        self.assertTrue("%s exists" % dataset, butler.datasetExists(datasetType=dataset, dataId=dataId))
        data = butler.get(dataset, dataId)
        if hasattr(data, '__subject__'):
            # Foil read proxy
            data = data.__subject__
        self.assertTrue("%s readable (%s)" % (dataset, data.__class__), data)

    @guard
    def validateSources(self, butler, dataId):
        src = butler.get('src', dataId)
        self.assertGreater("Number of sources", len(src), self.minSources)

    @guard
    def validateMatches(self, butler, dataId):
        matches = measAstrom.readMatches(butler, dataId)
        self.assertGreater("Number of matches", len(matches), self.minMatches)

    def validateCcd(self, butler, dataId):
        for ds in self.datasets:
            self.log.write("*** Validating %s for %s\n" % (ds, dataId))
            self.validateDataset(butler, dataId, ds)
                
        self.log.write("*** Validating source output for %s\n" % dataId)
        self.validateSources(butler, dataId)
        self.log.write("*** Validating matches output for %s\n" % dataId)
        self.validateMatches(butler, dataId)

