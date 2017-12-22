from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow, range, round, str,
                      super, zip)

from agstools._helpers import create_argument_groups, execute_args

def create_parser_machine_start(parser, parents):
    parser_start = parser.add_parser("machinestart", parents = parents, add_help = False,
        help = "Starts a machine on an ArcGIS Server instance.")
    parser_start.set_defaults(func = execute_args, lib_func = start_machine)

def start_machine(restadmin, name):
    machine = restadmin.machines.get(name)

    print("Starting machine...")
    machine.start()
    print("Machine started.")