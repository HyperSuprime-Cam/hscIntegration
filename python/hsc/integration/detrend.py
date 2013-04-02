import os, os.path
from hsc.integration.test import PbsTest
from hsc.integration.ccdValidation import ButlerValidationTest
from hsc.integration.camera import getCameraInfo

import lsst.afw.image.utils as afwIU


class ReduceDetrendsTest(PbsTest, ButlerValidationTest):
    def __init__(self, name, camera, detrend, idDict, detrendIdDict, dataIdList, rerun, time=1200, **kwargs):
        self.camera = camera
        self.detrend = detrend
        self.rerun = rerun
        self.dataIdList = dataIdList

        exeNames = {'bias': 'reduceBias.py',
                    'dark': 'reduceDark.py',
                    'flat': 'reduceFlat.py',
                    }

        if not detrend in exeNames:
            raise RuntimeError("Unrecognised detrend type: %s vs %s" % (detrend, exeNames.keys()))

        cameraInfo = getCameraInfo(self.camera)

        command = os.path.join(os.environ['HSCPIPE_DIR'], 'bin', exeNames[detrend]) + " "
        command += " @WORKDIR@/" + cameraInfo.addDir + " "
        command += " --id " + " ".join("=".join(map(str,kv)) for kv in idDict.items())
        command += " --detrendId " + " ".join("=".join(map(str,kv)) for kv in detrendIdDict.items())
        command += " --job=" + name
        command += " --time=%f" % time
        command += " @PBSARGS@"
        command += " --rerun=" + rerun

        # XXX The calibs used to end up in the root CALIB directory, but since Jim changed the rerun handling,
        # they go in a new rerun CALIB directory.  I'm more concerned to get things working than fix things up,
        # so here's a workaround.
#        create = "mkdir -p @WORKDIR@/" + cameraInfo.addDir + "/CALIB"
#        link = "ln -s ../rerun/" + detrend + "/CALIB/" + detrend.upper()
#        link += " @WORKDIR@/" + cameraInfo.addDir + "/CALIB/" + detrend.upper()

        super(ReduceDetrendsTest, self).__init__(name, ["pbs", "calib", detrend, camera],
                                                 [command], **kwargs)

#    def preHook(self, workDir=".", **kwargs):
#        suprimeDataDir = os.path.split(os.path.abspath(workDir))
#        if suprimeDataDir[-1] in ("SUPA", "HSC"):
#            # hsc.pipe.base.camera.getButler will add this directory on
#            suprimeDataDir = suprimeDataDir[:-1]
#        os.environ['SUPRIME_DATA_DIR'] = os.path.join(*suprimeDataDir)

    def validate(self, workdir=".", **kwargs):
        self.validatePbs()

        cameraInfo = getCameraInfo(self.camera)
        butler = hscCamera.getButler(self.camera, rerun=self.rerun,
                                     root=os.path.join(workDir, cameraInfo.addDir))
        for dataId in self.dataIdList:
            self.validateDataset(butler, dataId, self.detrend)

    def postHook(self, **kwargs):
        afwIU.resetFilters() # So other cameras may be run
