from __future__ import print_function, unicode_literals, absolute_import

from agstools._helpers import execute_args

def create_parser_stop(parser, parents):
    parser_stop = parser.add_parser("stop", parents = parents, add_help = False,
        help = "Stops a service on an ArcGIS Server instance.")
    parser_stop.set_defaults(func = execute_args, lib_func = stop_service)

def stop_service(restadmin, name, type, folder):
    serv = restadmin.get_service(name, type, folder)

    print("Stopping service...")
    serv.stop_service()
    print("Service stopped.")