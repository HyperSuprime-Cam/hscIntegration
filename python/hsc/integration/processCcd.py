import os, os.path
from hsc.integration.integration import CommandsTest

import hsc.pipe.base.camera as hscCamera
import lsst.meas.astrom.astrom as measAstrom


class ProcessCcdTest(CommandsTest):
    def __init__(self, name, camera, visit, ccd, dir=None, rerun=None, minMatches=30, minSources=1000,
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
        if rerun is not None:
            command += " --rerun=" + rerun
        
        super(ProcessCcdTest, self).__init__(name, [command])
        
    def validate(self):
        butler = hscCamera.getButler(self.camera, rerun=self.rerun, root=self.dir)

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
