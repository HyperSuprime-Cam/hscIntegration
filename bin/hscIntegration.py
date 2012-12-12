#!/usr/bin/env python

import os.path
import argparse
<<<<<<< /Users/price/hsc/hscIntegration/bin/hscIntegration.py
from hsc.integration import Integration
=======
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
Integration.register(ReduceDetrendsTest("scDetrend", "suprimecam", "flat", range(108390, 108401),
                                        rerun="detrend"))
Integration.register(CalibTest("scCalib", "suprimecam", validity=90))
Integration.register(ProcessCcdTest("SUPA01087235", "suprimecam", 108723, 5, rerun="processCcd"))
Integration.register(ProcessCcdTest("onsite", "suprimecam", 108723, 0, rerun="onsite",
                                    addOptions="-C " + os.path.join(hscPipeDir, 'config', 'onsite.py')))
Integration.register(ReduceFramesTest("reduceFrames-SC", "suprimecam", [108723, 108724, 108725],
                                      rerun="reduceFrames", time=4000))
Integration.register(SolveTansipTest("solvetansip", "suprimecam", 108723, rerun="reduceFrames"))
Integration.register(ReduceStackTest("reduceStack-SC", "suprimecam", "SDSS1115", "W-S-I+",
                                     rerun="reduceFrames"))
#Integration.register(PipeQaTest("pipeQa-SC", "suprimecam", [108723, 108724, 108725], "reduceFrames",
#                                "pipeQa-SC"))

# HSC tests
Integration.register(DataTest("hscData", "hscSim", os.path.join(dataDir, 'HSC')))
Integration.register(CalibTest("hscCalib", "hscSim", os.path.join(dataDir, 'HSC-Calib')))
Integration.register(ProcessCcdTest("HSCA00003100", "hscSim", 3, 100, rerun="processCcd"))
Integration.register(ReduceFramesTest("HSCA00003XXX", "hscSim", [3], rerun="reduceFrames", time=40000))
>>>>>>> /var/folders/f_/zxjlcs790p3f2z41k6qp5_k80000gp/T/hscIntegration.py~other.6bPEic

parser = argparse.ArgumentParser()
parser.add_argument("--only", action="append", choices=Integration.getTests(),
                    help="Only execute specified tests")
parser.add_argument("--deactivate", action="append", choices=Integration.getKeywords(),
                    help="Deactivate tests with this keyword")
parser.add_argument("--output", type=str, default=".", help="Output path")
parser.add_argument("--nodes", type=int, default=4, help="Number of nodes for PBS")
parser.add_argument("--procs", type=int, default=8, help="Number of processors per node for PBS")
args = parser.parse_args()

Integration(args.only, args.deactivate).run(workDir=args.output, nodes=args.nodes, procs=args.procs)
