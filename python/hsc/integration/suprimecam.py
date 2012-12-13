import os
from hsc.integration.integration import Integration
from hsc.integration.processCcd import ProcessCcdTest
from hsc.integration.reduceFrames import ReduceFramesTest
from hsc.integration.reduceStack import ReduceStackTest
from hsc.integration.detrend import ReduceDetrendsTest
from hsc.integration.data import DataTest, CalibTest
from hsc.integration.solvetansip import SolveTansipTest
from hsc.integration.pipeQa import PipeQaTest

#from hsc.integration.database import DbCreateTest, DbRawTest

dataDir = os.environ['HSCINTEGRATIONDATA_DIR']
hscPipeDir = os.environ['HSCPIPE_DIR']

# Suprime-Cam tests
#Integration.register(DbCreateTest("scDbCreate", "suprimecam", "Raw_Sup", "localhost",
#                                  "hscIntegration_sc", os.getlogin(), os.getlogin()))
#Integration.register(DbRawTest("scDbRaw", "suprimecam", "localhost", "hscIntegration_sc", os.getlogin(),
#                               os.getlogin(), os.path.join(dataDir, 'SuprimeCam')))



Integration.register(DataTest("scData", "suprimecam", os.path.join(dataDir, 'SuprimeCam')))
#Integration.register(ReduceDetrendsTest("scBias", "suprimecam", "bias", {'field': 'BIAS'},
#                                        {'calibVersion': 0}, rerun="bias"))
#Integration.register(CalibTest("scCalibBias", "suprimecam", validity=90))
Integration.register(ReduceDetrendsTest("scFlat", "suprimecam", "flat", {'field': 'DOMEFLAT'},
                                        {'calibVersion': "one"}, rerun="flat"))
Integration.register(CalibTest("scCalibFlat", "suprimecam", validity=90))
Integration.register(ProcessCcdTest("SUPA01087235", "suprimecam", 108723, 5, rerun="processCcd"))
Integration.register(ProcessCcdTest("onsite", "suprimecam", 108723, 0, rerun="onsite",
                                    addOptions="-C " + os.path.join(hscPipeDir, 'config', 'onsite.py')))
Integration.register(ReduceFramesTest("reduceFrames-SC", "suprimecam", [{'visit': '108723..108725'}],
                                      [{'visit': v, 'ccd': c} for v in (108723, 108724, 108725)
                                       for c in range(10)], rerun="reduceFrames", time=4000))
Integration.register(SolveTansipTest("solvetansip", "suprimecam", 108723, rerun="reduceFrames"))
Integration.register(ReduceStackTest("reduceStack-SC", "suprimecam", "SDSS1115", "W-S-I+",
                                     rerun="reduceFrames"))
#Integration.register(PipeQaTest("pipeQa-SC", "suprimecam", [108723, 108724, 108725], "reduceFrames",
#                                "pipeQa-SC"))
