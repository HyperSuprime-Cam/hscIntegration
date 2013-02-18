import os, os.path
from hsc.integration.test import PbsTest
from hsc.integration.camera import getCameraInfo
from hsc.integration.ccdValidation import CcdValidationTest

import hsc.pipe.base.camera as hscCamera
import lsst.afw.image.utils as afwIU

class ReduceStackTest(PbsTest):
    def __init__(self, name, camera, field, filtName, time=10000, rerun=None, **kwargs):
        self.camera = camera
        self.field = field
        self.filtName = filtName
        self.rerun = rerun

        command = os.path.join(os.environ['HSCPIPE_DIR'], 'bin', 'reduceStack.py') + " "
        command += " --job=" + name
        command += " --instrument=" + camera
        command += " @PBSARGS@"
        command += " --time=%f" % time
        if rerun is not None:
            command += " --rerun=" + rerun
        command += " " + field + " " + filtName
        
        super(ReduceStackTest, self).__init__(name, ["pbs", "stack", camera], [command], **kwargs)

    def preHook(self, workDir=".", **kwargs):
        suprimeDataDir = os.path.split(os.path.abspath(workDir))
        if suprimeDataDir[-1] in ("SUPA", "HSC"):
            # hsc.pipe.base.camera.getButler will add this directory on
            suprimeDataDir = suprimeDataDir[:-1]
        os.environ['SUPRIME_DATA_DIR'] = os.path.join(*suprimeDataDir)

    def validate(self, workDir=".", **kwargs):
        self.validatePbs()

        cameraInfo = getCameraInfo(self.camera)
        butler = hscCamera.getButler(self.camera, rerun=self.rerun,
                                     root=os.path.join(workDir, cameraInfo.addDir))

    def postHook(self, **kwargs):
        afwIU.resetFilters() # So other cameras may be run        
