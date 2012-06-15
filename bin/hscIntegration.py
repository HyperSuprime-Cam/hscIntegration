#!/usr/bin/env python

import os.path
from hsc.integration.integration import Integrator
from hsc.integration.processCcd import ProcessCcdTest
from hsc.integration.data import DataTest

integrator = Integrator(tests=[
    DataTest("scData", "suprimecam", os.path.join(os.environ['HSCINTEGRATIONDATA_DIR'], 'SuprimeCam'), 'DATA'),
    ProcessCcdTest("SUPA01269695", "suprimecam", 126969, 5, dir='DATA/SUPA', rerun="test"),
    ])

integrator.run()
