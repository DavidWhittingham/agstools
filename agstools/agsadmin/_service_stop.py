from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow, range, round, str,
                      super, zip)

from agstools._helpers import execute_args

def create_parser_service_stop(parser, parents):
    parser_stop = parser.add_parser("servicestop", parents = parents, add_help = False,
        help = "Stops a service on an ArcGIS Server instance.")
    parser_stop.set_defaults(func = execute_args, lib_func = stop_service)

def stop_service(restadmin, name, type, folder):
    serv = restadmin.services.get_service(name, type, folder)

    print("Stopping service...")
    serv.stop_service()
    print("Service stopped.")