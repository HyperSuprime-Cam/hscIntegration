import os, os.path
from hsc.integration.integration import CommandsTest
from hsc.integration.ccdValidation import CcdValidationTest

import hsc.pipe.base.camera as hscCamera
import lsst.afw.image.utils as afwIU


class ProcessCcdTest(CommandsTest, CcdValidationTest):
    def __init__(self, name, camera, visit, ccd, dir=None, rerun=None, **kwargs):
        self.camera = camera
        self.visit = visit
        self.ccd = ccd
        self.dataId = {'visit': visit, 'ccd': ccd}
        self.dir = dir if dir is not None else os.environ['HSCINTEGRATIONDATA_DIR']
        self.rerun = rerun

        command = os.path.join(os.environ['HSCPIPE_DIR'], 'bin', 'scProcessCcd.py') + \
                  " " + camera + " " + self.dir + " --doraise --id visit=%d ccd=%d" % (self.visit, self.ccd)
        if rerun is not None:
            command += " --rerun=" + rerun
        
        super(ProcessCcdTest, self).__init__(name, [command], **kwargs)
        
    def validate(self):
        butler = hscCamera.getButler(self.camera, rerun=self.rerun, root=self.dir)
        self.validateCcd(butler, self.dataId)

        afwIU.resetFilters() # So other cameras may be run        



