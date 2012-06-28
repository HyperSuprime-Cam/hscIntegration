#!/usr/bin/env python

import os.path
from hsc.integration.integration import Integrator
from hsc.integration.processCcd import ProcessCcdTest
from hsc.integration.reduceFrames import ReduceFramesTest
from hsc.integration.data import DataTest, CalibTest

integrator = Integrator(tests=[
#    DataTest("scData", "suprimecam", os.path.join(os.environ['HSCINTEGRATIONDATA_DIR'], 'SuprimeCam'),
#             'DATA'),
#    CalibTest("scCalib", "suprimecam", os.path.join(os.environ['HSCINTEGRATIONDATA_DIR'], 'SC-Calib'), 
#              'DATA/SUPA/CALIB', validity=90),
#    ProcessCcdTest("SUPA01087235", "suprimecam", 108723, 5, dir='DATA/SUPA', rerun="processCcd"),
#
#    DataTest("hscData", "hscsim", os.path.join(os.environ['HSCINTEGRATIONDATA_DIR'], 'HSC'), 'DATA'),
#    CalibTest("hscCalib", "hscsim", os.path.join(os.environ['HSCINTEGRATIONDATA_DIR'], 'HSC-Calib'),
#              'DATA/HSC/CALIB'),
#    ProcessCcdTest("HSCA00243100", "hscsim", 243, 100, dir='DATA/HSC', rerun="processCcd"),
#
    ReduceFramesTest("SUPA0108723X", "suprimecam", [108723], dir='DATA/SUPA', rerun="reduceFrames")
    ])


integrator.run()
