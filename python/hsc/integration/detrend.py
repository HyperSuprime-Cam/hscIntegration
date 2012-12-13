import os, os.path
from hsc.integration.test import PbsTest
from hsc.integration.ccdValidation import CcdValidationTest

import hsc.pipe.base.camera as hscCamera
import lsst.afw.image.utils as afwIU


class ReduceDetrendsTest(PbsTest, CcdValidationTest):
    def __init__(self, name, camera, detrend, idDict, detrendIdDict, time=1200, rerun=None, **kwargs):
        self.camera = camera
        self.detrend = detrend
        self.rerun = rerun

        exeNames = {'bias': 'reduceBias.py',
                    'dark': 'reduceDark.py',
                    'flat': 'reduceFlat.py',
                    }

        if not detrend in exeNames:
            raise RuntimeError("Unrecognised detrend type: %s vs %s" % (detrend, exeNames.keys()))

        command = os.path.join(os.environ['HSCPIPE_DIR'], 'bin', exeNames[detrend]) + " "
        command += " " + camera + " @WORKDIR@ "
        command += " --id " + " ".join("=".join(kv) for kv in idDict.items())
        command == " --detrendId " + " ".join("=".join(kv) for kv in detrendIdDict.items())
        command += " --job=" + name
        command += " --time=%f" % time
        if rerun is not None:
            command += " --rerun=" + rerun
        command += " @PBSARGS@"

        super(ReduceDetrendsTest, self).__init__(name, ["pbs", "calib", detrend, camera], [command], **kwargs)

#    def preHook(self, workDir=".", **kwargs):
#        suprimeDataDir = os.path.split(os.path.abspath(workDir))
#        if suprimeDataDir[-1] in ("SUPA", "HSC"):
#            # hsc.pipe.base.camera.getButler will add this directory on
#            suprimeDataDir = suprimeDataDir[:-1]
#        os.environ['SUPRIME_DATA_DIR'] = os.path.join(*suprimeDataDir)

    def validate(self, **kwargs):
        self.validatePbs()
        # XXX additional validation?

    def postHook(self, **kwargs):
        afwIU.resetFilters() # So other cameras may be run
