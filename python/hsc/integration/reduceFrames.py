import os, os.path
from hsc.integration.integration import PbsTest
from hsc.integration.ccdValidation import CcdValidationTest

import hsc.pipe.base.camera as hscCamera
import lsst.afw.image.utils as afwIU

class ReduceFramesTest(PbsTest, CcdValidationTest):
    def __init__(self, name, camera, visits, nodes=4, procs=8, time=1200, queue=None, dir=None, rerun=None,
                 **kwargs):
        self.camera = camera
        self.visits = visits
        self.dir = dir if dir is not None else os.environ['HSCINTEGRATIONDATA_DIR']
        self.rerun = rerun

        suprimeDataDir = os.path.split(os.path.abspath(self.dir))
        if suprimeDataDir[-1] in ("SUPA", "HSC"):
            # hsc.pipe.base.camera.getButler will add this directory on
            suprimeDataDir = suprimeDataDir[:-1]
        os.environ['SUPRIME_DATA_DIR'] = os.path.join(*suprimeDataDir)

        command = os.path.join(os.environ['HSCPIPE_DIR'], 'bin', 'reduceFrames.py') + " "
        command += " --job=" + name
        command += " --instrument=" + camera
        command += " --nodes=%d" % nodes
        command += " --procs=%d" % procs
        command += " --time=%f" % time
        if rerun is not None:
            command += " --rerun=" + rerun
        if queue is not None:
            command += "--queue=" + queue
        command += " " + ' '.join(map(str, visits))
        
        super(ReduceFramesTest, self).__init__(name, [command], **kwargs)

    def validate(self):
        self.validatePbs()
        
        butler = hscCamera.getButler(self.camera, rerun=self.rerun, root=self.dir)
        numCcds = hscCamera.getNumCcds(self.camera)

        for visit in self.visits:
            for ccd in range(numCcds):
                dataId = {'visit': visit, 'ccd': ccd}
                self.validateCcd(butler, dataId)

        afwIU.resetFilters() # So other cameras may be run        
