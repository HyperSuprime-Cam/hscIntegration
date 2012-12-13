import os, os.path
from hsc.integration.test import PbsTest
from hsc.integration.camera import getCameraInfo
from hsc.integration.ccdValidation import CcdValidationTest

import hsc.pipe.base.camera as hscCamera
import lsst.afw.image.utils as afwIU

class ReduceFramesTest(PbsTest, CcdValidationTest):
    def __init__(self, name, camera, idDictList, dataIdList, time=1200, rerun=None, **kwargs):
        self.camera = camera
        self.idDictList = idDictList
        self.dataIdList = dataIdList
        self.rerun = rerun

        command = os.path.join(os.environ['HSCPIPE_DIR'], 'bin', 'reduceFrames.py')
        command += " " + camera + " @WORKDIR@ "
        command += " --id ".join(" ".join("=".join(kv) for kv in idDict.items()) for idDict in idDictList)
        command += " --job=" + name
        command += " --time=%f" % time
        if rerun is not None:
            command += " --rerun=" + rerun
        command += " @PBSARGS@"

        super(ReduceFramesTest, self).__init__(name, [command], keywords=["pbs", "process", camera], **kwargs)

#    def preHook(self, workDir=".", **kwargs):
#        suprimeDataDir = os.path.split(os.path.abspath(workDir))
#        if suprimeDataDir[-1] in ("SUPA", "HSC"):
#            # hsc.pipe.base.camera.getButler will add this directory on
#            suprimeDataDir = suprimeDataDir[:-1]
#        os.environ['SUPRIME_DATA_DIR'] = os.path.join(*suprimeDataDir)

    def validate(self, workDir=".", **kwargs):
        self.validatePbs()
        
        cameraInfo = getCameraInfo(self.camera)
        butler = hscCamera.getButler(self.camera, rerun=self.rerun,
                                     root=os.path.join(workDir, cameraInfo.addDir))
        numCcds = hscCamera.getNumCcds(self.camera)

        for dataId in self.dataIdList:
            self.validateCcd(butler, dataId)

    def postHook(self, **kwargs):
        afwIU.resetFilters() # So other cameras may be run
