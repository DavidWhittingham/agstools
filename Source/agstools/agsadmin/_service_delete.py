from __future__ import print_function, unicode_literals, absolute_import

from agstools._helpers import execute_args

def create_parser_service_delete(parser, parents):
    """Creates a sub-parser for deleting an ArcGIS Server Service."""

    parser_delete = parser.add_parser("servicedelete", parents = parents, add_help = False,
        help = "Deletes a service on an ArcGIS Server instance.")
    parser_delete.set_defaults(func = execute_args, lib_func = delete_service)

def delete_service(restadmin, name, type, folder):
    print("Deleting service...")
    restadmin.delete_service(name, type, folder)
    print("Service deleted.")