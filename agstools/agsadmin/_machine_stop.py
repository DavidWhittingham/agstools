from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow, range, round, str,
                      super, zip)

from agstools._helpers import create_argument_groups, execute_args

def create_parser_machine_stop(parser, parents):
    parser_stop = parser.add_parser("machinestop", parents = parents, add_help = False,
        help = "Stops a machine on an ArcGIS Server instance.")
    parser_stop.set_defaults(func = execute_args, lib_func = stop_machine)

def stop_machine(restadmin, name):
    machine = restadmin.machines.get(name)

    print("Stopping machine...")
    machine.stop()
    print("Machine stopped.")