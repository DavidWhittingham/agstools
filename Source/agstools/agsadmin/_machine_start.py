from __future__ import print_function, unicode_literals, absolute_import

from agstools._helpers import create_argument_groups, execute_args

def create_parser_machine_start(parser, parents):
    parser_start = parser.add_parser("machinestart", parents = parents, add_help = False,
        help = "Starts a machine on an ArcGIS Server instance.")
    parser_start.set_defaults(func = execute_args, lib_func = start_machine)

def start_machine(restadmin, name):
    machine = restadmin.get_machine(name)

    print("Starting machine...")
    machine.start()
    print("Machine started.")