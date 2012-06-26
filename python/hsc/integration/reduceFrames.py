import os, os.path
from hsc.integration.integration import PbsTest

import hsc.pipe.base.camera as hscCamera
import lsst.meas.astrom.astrom as measAstrom
import lsst.afw.image.utils as afwIU

class ReduceFramesTest(PbsTest):
    def __init__(self, name, camera, visits, nodes=2, procs=8, time=120, queue=None, dir=None, rerun=None,
                 minMatches=30, minSources=1000,
                 datasets=["icSrc", "icMatch", "psf", "apCorr", "src", "calexp"]
                 ):
        self.camera = camera
        self.visits = visits
        self.dir = dir if dir is not None else os.environ['HSCINTEGRATIONDATA_DIR']
        self.rerun = rerun
        self.minMatches = minMatches
        self.minSources = minSources
        self.datasets = set(datasets)

        os.environ['SUPRIME_DATA_DIR'] = dir if dir is not None else os.environ['HSCINTEGRATIONDATA_DIR']

        command = os.path.join(os.environ['HSCPIPE_DIR'], 'bin', 'reduceFrames.py') + " "
        command += " --job=" + name
        command += " --instrument=" + camera
        command += " --nodes=%d" % nodes
        command += " --procs=%d" % procs
        command += " --time=%f" % time
        if dir is not None:
            command += " --output=%s" % dir
        if rerun is not None:
            command += " --rerun=" + rerun
        if queue is not None:
            command += "--queue=" + queue
        command += " ".join(map(str, visits))
        
        super(ProcessCcdTest, self).__init__(name, [command])
        
    def validate(self):
        butler = hscCamera.getButler(self.camera, rerun=self.rerun, root=self.dir)
        numCcds = hscCamera.getNumCcds(self.camera)

        for visit in visits:
            for ccd in range(numCcds):
                dataId = {'visit': visit, 'ccd': ccd}
                for ds in self.datasets:
                    self.assertTrue("%s exists" % ds, butler.datasetExists(datasetType=ds, dataId=dataId))
                    data = butler.get(ds, dataId)
                    if hasattr(data, '__subject__'):
                        # Foil read proxy
                        data = data.__subject__
                    self.assertTrue("%s readable (%s)" % (ds, data.__class__), data)

                src = butler.get('src', dataId)
                self.assertGreater("Number of sources", len(src), self.minSources)

                matches = measAstrom.readMatches(butler, dataId)
                self.assertGreater("Number of matches", len(matches), self.minMatches)

        afwIU.resetFilters() # So other cameras may be run        
