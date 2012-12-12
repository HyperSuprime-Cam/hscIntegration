import os, os.path
from hsc.integration.test import PbsTest
from hsc.integration.ccdValidation import CcdValidationTest

import hsc.pipe.base.camera as hscCamera
import lsst.afw.image.utils as afwIU

class ReduceDetrendsTest(PbsTest, CcdValidationTest):
    def __init__(self, name, camera, detrend, visits, time=1200, queue=None, rerun=None,
                 **kwargs):
        self.camera = camera
        self.visits = visits
        self.detrend = detrend
        self.rerun = rerun

        command = os.path.join(os.environ['HSCPIPE_DIR'], 'bin', 'reduceDetrends.py') + " "
        command += " --job=" + name
        command += " --instrument=" + camera
        command += " --nodes=@NODES@"
        command += " --procs=@PROCS@"
        command += " --time=%f" % time
        command += " --detrend=" + detrend
        if rerun is not None:
            command += " --rerun=" + rerun
        if queue is not None:
            command += "--queue=" + queue
        command += " " + ' '.join(map(str, visits))
        
        super(ReduceDetrendsTest, self).__init__(name, [command], keywords=["pbs", "calib", camera], **kwargs)

    def preHook(self, workDir=".", **kwargs):
        suprimeDataDir = os.path.split(os.path.abspath(workDir))
        if suprimeDataDir[-1] in ("SUPA", "HSC"):
            # hsc.pipe.base.camera.getButler will add this directory on
            suprimeDataDir = suprimeDataDir[:-1]
        os.environ['SUPRIME_DATA_DIR'] = os.path.join(*suprimeDataDir)

    def validate(self, **kwargs):
        self.validatePbs()
        # XXX additional validation?

    def postHook(self, **kwargs):
        afwIU.resetFilters() # So other cameras may be run        
