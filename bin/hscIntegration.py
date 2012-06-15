#!/usr/bin/env python

import os.path
from hsc.integration.integration import Integrator
from hsc.integration.processCcd import ProcessCcdTest
from hsc.integration.data import DataTest, CalibTest

integrator = Integrator(tests=[
    DataTest("scData", "suprimecam", os.path.join(os.environ['HSCINTEGRATIONDATA_DIR'], 'SuprimeCam'), 'DATA'),
    CalibTest("scCalib", "suprimecam", os.path.join(os.environ['HSCINTEGRATIONDATA_DIR'], 'SUPA', 'CALIB'), 
              'DATA/SUPA/CALIB', validity=90),
    ProcessCcdTest("SUPA01087235", "suprimecam", 108723, 5, dir='DATA/SUPA', rerun="test"),
    ])

integrator.run()
