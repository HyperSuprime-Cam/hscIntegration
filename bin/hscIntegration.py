#!/usr/bin/env python

import os.path
import argparse
from hsc.integration.integration import Integration
from hsc.integration.processCcd import ProcessCcdTest
from hsc.integration.reduceFrames import ReduceFramesTest
from hsc.integration.data import DataTest, CalibTest

dataDir = os.environ['HSCINTEGRATIONDATA_DIR']

# Suprime-Cam tests
Integration.register(DataTest("scData", "suprimecam", os.path.join(dataDir, 'SuprimeCam')))
Integration.register(CalibTest("scCalib", "suprimecam", os.path.join(dataDir, 'SC-Calib'), validity=90))
Integration.register(ProcessCcdTest("SUPA01087235", "suprimecam", 108723, 5, rerun="processCcd"))
Integration.register(ReduceFramesTest("SUPA0108723X", "suprimecam", [108723], rerun="reduceFrames"))

# HSC tests
Integration.register(DataTest("hscData", "hscsim", os.path.join(dataDir, 'HSC')))
Integration.register(CalibTest("hscCalib", "hscsim", os.path.join(dataDir, 'HSC-Calib')))
Integration.register(ProcessCcdTest("HSCA00243100", "hscsim", 243, 100, rerun="processCcd"))
Integration.register(ReduceFramesTest("HSCA00243XXX", "hsc", [243], rerun="reduceFrames", time=12000))

parser = argparse.ArgumentParser()
parser.add_argument("--no-suprimecam", dest="noSC", default=False, action="store_true",
                    help="Don't process Suprime-Cam data?")
parser.add_argument("--no-hsc", dest="noHSC", default=False, action="store_true",
                    help="Don't process HSC data?")
parser.add_argument("--no-pbs", dest="noPBS", default=False, action="store_true",
                    help="Don't execute PBS jobs?")
parser.add_argument("--existing", default=False, action="store_true", help="Use existing data setup?")
parser.add_argument("--output", type=str, default=".", help="Output path")
args = parser.parse_args()

suprimecamTests = {"scData", "scCalib", "SUPA01087235", "SUPA0108723X"}
hscTests = {"hscData", "hscCalib", "HSCA00243100", "HSCA00243XXX"}
pbsTests = {"SUPA0108723X", "HSCA00243XXX"}
dataTests = {"scData", "scCalib", "hscData", "hscCalib"}

exclude = set()
if args.noSC:
    exclude |= suprimecamTests
if args.noHSC:
    exclude |= hscTests
if args.noPBS:
    exclude |= pbsTests
if args.existing:
    exclude |= dataTests

Integration(exclude).run(workDir=args.output)
