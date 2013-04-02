import os, os.path
from hsc.integration.test import Test, guard
import lsst.meas.astrom.astrom as measAstrom

positive = lambda x: x > 0
nonEmpty = lambda s: len(s) > 0

class ButlerValidationTest(Test):
    """Mix-in class to validate butler retrieval"""
    @guard
    def validateDataset(self, butler, dataId, dataset):
        self.assertTrue("%s exists" % dataset, butler.datasetExists(datasetType=dataset, dataId=dataId))
        data = butler.get(dataset, dataId)
        if hasattr(data, '__subject__'):
            # Foil read proxy
            data = data.__subject__
        self.assertTrue("%s readable (%s)" % (dataset, data.__class__), data)

    @guard
    def validateFile(self, butler, dataId, dataset):
        filename = butler.get(dataset + "_filename", dataId)[0]
        self.assertTrue("%s exists on disk" % dataset, os.path.exists(filename))
        self.assertGreater("%s has non-zero size" % dataset, os.stat(filename).st_size, 0)



class CcdValidationTest(ButlerValidationTest):
    """Mix-in class to validate a CCD"""
    def __init__(self, name, keywords, minMatches=10, minSources=100,
                 datasets=["icSrc", "icMatch", "psf", "src", "calexp", "icMatchFull", "srcMatch",
                           "srcMatchFull", ],
                 files=["ossThumb", "flattenedThumb", "plotMagHist", "plotSeeingRough",
                        "plotSeeingRobust", "plotSeeingMap", "plotEllipseMap", "plotEllipticityMap",
                        "plotFwhmGrid", "plotEllipseGrid", "plotEllipticityGrid"],
                 metadataExist=['FLAG_AUTO', 'FLAG_USR', 'FLAG_TAG',
                                'ELL_MED', 'ELL_PA_MED',
                                ],
                 metadataValidate={'NOBJ_BRIGHT': positive,
                                   'NOBJ_MATCHED': positive,
                                   'WCS_NOBJ': positive,
                                   'WCS_SIPORDER': positive,
                                   'WCS_RMS': positive,
                                   'RERUN': nonEmpty,
                                   'MAGZERO': positive,
                                   'MAGZERO_RMS': positive,
                                   'MAGZERO_NOBJ': positive,
                                   'OSLEVEL1': positive,
                                   'OSLEVEL2': positive,
                                   'OSLEVEL3': positive,
                                   'OSLEVEL4': positive,
                                   'OSSIGMA1': positive,
                                   'OSSIGMA2': positive,
                                   'OSSIGMA3': positive,
                                   'OSSIGMA4': positive,
                                   'SKYLEVEL': positive,
                                   'SKYSIGMA': positive,
                                   'FLATNESS_PP': positive,
                                   'FLATNESS_RMS': positive,
                                   'FLATNESS_NGRIDS': positive,
                                   'FLATNESS_MESHX': positive,
                                   'FLATNESS_MESHY': positive,
                                   'SEEING_MODE': positive,
                                   },
                 **kwargs):
        super(CcdValidationTest, self).__init__(name, keywords, **kwargs)
        self.minMatches = minMatches
        self.minSources = minSources
        self.datasets = set(datasets)
        self.files = set(files)
        self.metadataExist = set(metadataExist)
        self.metadataValidate = metadataValidate

    @guard
    def validateSources(self, butler, dataId):
        src = butler.get('src', dataId)
        self.assertGreater("Number of sources", len(src), self.minSources)

    @guard
    def validateMatches(self, butler, dataId):
        matches = measAstrom.readMatches(butler, dataId)
        self.assertGreater("Number of matches", len(matches), self.minMatches)

    @guard
    def assertMetadata(self, metadata, key, validate=None):
        exists = key in metadata.names()
        self.assertTrue("Metadata %s exists" % key, exists)
        if validate is not None and exists:
            value = metadata.get(key)
            self.assertTrue("Metadata %s validation (%s)" % (key, value), validate(value))

    @guard
    def validateExposure(self, butler, dataId):
        exp = butler.get("calexp", dataId)
        md = exp.getMetadata()
        for key in self.metadataExist:
            self.assertMetadata(md, key)
        for key, validate in self.metadataValidate.iteritems():
            self.assertMetadata(md, key, validate)


    def validateCcd(self, butler, dataId):
        for ds in self.datasets:
            self.log.write("*** Validating dataset %s for %s\n" % (ds, dataId))
            self.validateDataset(butler, dataId, ds)

        for f in self.files:
            self.log.write("*** Validating file %s for %s\n" % (f, dataId))
            self.validateFile(butler, dataId, f)

        self.log.write("*** Validating exposure output for %s\n" % dataId)
        self.validateExposure(butler, dataId)

        self.log.write("*** Validating source output for %s\n" % dataId)
        self.validateSources(butler, dataId)
        self.log.write("*** Validating matches output for %s\n" % dataId)
        self.validateMatches(butler, dataId)

