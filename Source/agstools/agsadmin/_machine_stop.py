from __future__ import print_function, unicode_literals, absolute_import

from agstools._helpers import create_argument_groups, execute_args

def create_parser_machine_stop(parser, parents):
    parser_stop = parser.add_parser("machinestop", parents = parents, add_help = False,
        help = "Stops a machine on an ArcGIS Server instance.")
    parser_stop.set_defaults(func = execute_args, lib_func = stop_machine)

def stop_machine(restadmin, name):
    machine = restadmin.get_machine(name)

    print("Stopping machine...")
    machine.stop()
    print("Machine stopped.")