#!/usr/bin/env python

from hsc.integration.integration import Integrator, ProcessCcdTest

integrator = Integrator(tests=[
    ProcessCcdTest("SUPA01269695", "suprimecam", 126969, 5, dir="/home/price/data/Subaru/SUPA", rerun="test"),
    ])

integrator.run()
