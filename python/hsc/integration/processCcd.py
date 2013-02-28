import os, os.path
from hsc.integration.test import CommandsTest
from hsc.integration.camera import getCameraInfo
from hsc.integration.ccdValidation import CcdValidationTest

import hsc.pipe.base.camera as hscCamera
import lsst.afw.image.utils as afwIU


class ProcessCcdTest(CommandsTest, CcdValidationTest):
    def __init__(self, name, camera, visit, ccd, rerun=None, addOptions="", **kwargs):
        self.camera = camera
        self.visit = visit
        self.ccd = ccd
        self.dataId = {'visit': visit, 'ccd': ccd}
        self.rerun = rerun

        cameraInfo = getCameraInfo(camera)
        command = os.path.join(os.environ['HSCPIPE_DIR'], 'bin', 'scProcessCcd.py') + \
                  " @WORKDIR@/" + cameraInfo.addDir + \
                  " --doraise " + addOptions + \
                  " --id visit=%d ccd=%d" % (self.visit, self.ccd)
        
        
        if rerun is not None:
            command += " --rerun=" + rerun
        
        super(ProcessCcdTest, self).__init__(name, ["process", camera], [command], **kwargs)
        
    def validate(self, workDir=".", **kwargs):
        cameraInfo = getCameraInfo(self.camera)
        butler = hscCamera.getButler(self.camera, rerun=self.rerun,
                                     root=os.path.join(workDir, cameraInfo.addDir))
        self.validateCcd(butler, self.dataId)

    def postHook(self, **kwargs):
        afwIU.resetFilters() # So other cameras may be run        



