import os
from hsc.integration.integration import Integration
from hsc.integration.processCcd import ProcessCcdTest
from hsc.integration.reduceFrames import ReduceFramesTest
from hsc.integration.reduceStack import ReduceStackTest
from hsc.integration.detrend import ReduceDetrendsTest
from hsc.integration.data import DataTest, CalibTest
from hsc.integration.solvetansip import SolveTansipTest
from hsc.integration.pipeQa import PipeQaTest

dataDir = os.environ['HSCINTEGRATIONDATA_DIR']


# This only includes a single visit to save time, but it does cover the focus and guide CCDs.
singleFrame = [{'visit': 902876, 'ccd': c} for c in range(112)]
# This only covers 104 CCDs because we explicitly drop all by the science CCDs in reduceFrames.
multiFrames = [{'visit': v, 'ccd': c} for v in range(902872, 902890, 2) for c in range(104)]

Integration.register(DataTest("hscData", "hsc", os.path.join(dataDir, 'HSC'), singleFrame))
Integration.register(ReduceDetrendsTest("hscBias", "hsc", "bias", {'field': 'BIAS'},
                                        {'calibVersion': "0"}, rerun="bias"))
Integration.register(CalibTest("hscCalibBias", "hsc", "bias", singleFrame, validity=90))
Integration.register(ReduceDetrendsTest("hscFlat", "hsc", "flat", {'field': 'DOMEFLAT'},
                                        {'calibVersion': "one"}, rerun="flat"))
Integration.register(CalibTest("hscCalibFlat", "hsc", "flat", singleFrame, validity=90))
Integration.register(ProcessCcdTest("HSC-902876-049", "hsc", 902876, 49, rerun="processCcd"))
Integration.register(ProcessCcdTest("HSC-902876-054", "hsc", 902876, 54, rerun="processCcd"))
Integration.register(ProcessCcdTest("HSC-902876-090", "hsc", 902876, 90, rerun="processCcd"))
Integration.register(ProcessCcdTest("HSC-902876-103", "hsc", 902876, 103, rerun="processCcd"))
Integration.register(ProcessCcdTest("HSC-902876-111", "hsc", 902876, 111, rerun="processCcd"))
Integration.register(ReduceFramesTest("reduceFrames-HSC", "hsc", [{'visit': '902876..902880:2'}],
                                      multiFrames, rerun="reduceFrames", time=300))
Integration.register(SolveTansipTest("solvetansip-HSC", "hsc", 902876, rerun="reduceFrames"))
Integration.register(ReduceStackTest("reduceStack-HSC", "hsc", "ABELL2163", "HSC-I",
                                     rerun="reduceFrames"))
