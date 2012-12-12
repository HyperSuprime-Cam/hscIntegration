#!/usr/bin/env python

import argparse
from hsc.integration import Integration

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
