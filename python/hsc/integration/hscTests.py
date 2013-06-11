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
hscPipeDir = os.environ['HSCPIPE_DIR']

readDataIdList = [{'visit': v, 'ccd': c} for v in (902042,) for c in range(112)]
processDataIdList = [dataId for dataId in readDataIdList if dataId['ccd'] < 104]

Integration.register(DataTest("hscData", "hsc", os.path.join(dataDir, 'HSC'), readDataIdList))
Integration.register(CalibTest("hscCalibFlat", "hsc", "flat", readDataIdList,
                               source=os.path.join(dataDir, 'HSC-Calib')))
Integration.register(ProcessCcdTest("HSCA902042049", "hsc", 902042, 49, rerun="processCcd"))
Integration.register(ProcessCcdTest("HSCA902042103", "hsc", 902042, 103, rerun="processCcd")) # rotated
Integration.register(ProcessCcdTest("HSCA902042111", "hsc", 902042, 111, rerun="processCcd")) # focus
Integration.register(ReduceFramesTest("reduceFrames-HSC", "hsc", [{'visit': '902042'}],
                                      processDataIdList, rerun="reduceFrames", time=100000))
Integration.register(SolveTansipTest("solvetansip-HSC", "hsc", 902042, rerun="reduceFrames"))
