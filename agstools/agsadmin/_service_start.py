from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow, range, round, str,
                      super, zip)

from agstools._helpers import execute_args

def create_parser_service_start(parser, parents):
    parser_start = parser.add_parser("servicestart", parents = parents, add_help = False,
        help = "Starts a service on an ArcGIS Server instance.")
    parser_start.set_defaults(func = execute_args, lib_func = start_service)

def start_service(restadmin, name, type, folder):
    serv = restadmin.services.get_service(name, type, folder)

    print("Starting service...")
    serv.start_service()
    print("Service started.")