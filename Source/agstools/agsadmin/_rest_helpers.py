from __future__ import print_function, unicode_literals, absolute_import

import argparse
import time

from agstools._helpers import create_argument_groups, execute_args

def create_parser_agsrest_parent():
    parser_agsrest_parent = argparse.ArgumentParser(add_help = False)
    parser_agsrest_parent.set_defaults(
        parse_for_restadmin = True,
        utc_delta = time.timezone / -60 if time.daylight == 0 else time.altzone / -60,
        instance = 'arcgis',
        port = 6080
    )

    group_req, group_opt, group_flags = create_argument_groups(parser_agsrest_parent)
    group_req.add_argument("-s", "--server", required = True,
        help = "The host name of the ArcGIS Server (e.g. myarcgisserver.local).")
    group_req.add_argument("-u", "--username", required = True,
        help = "The username of an account with appropriate privileges on the ArcGIS server instance.")
    group_req.add_argument("-p", "--password", required = True,
        help = "Password for the user account")

    group_opt.add_argument("-i", "--instance",
        help = "The instance name of the ArcGIS Server (defaults to 'arcgis').")
    group_opt.add_argument("--port", type = int,
        help = "The port number to use when communicating with the ArcGIS Server instance (default is 6080).")
    group_opt.add_argument("--proxy",
        help = "Address of a proxy server, if one is required to communicate with the ArcGIS Server.")
    group_opt.add_argument("--utc-delta", type=int,
        help = "The number of minutes (plus/minus) your server is from UTC. This is used when calculating key expiry \
            time when performing non-SSL encrypted communications. Defaults to your local offset.")

    group_flags.add_argument("--ssl", action = "store_true",
        help = "Forces the use of TLS/SSL when processing the request.")

    return parser_agsrest_parent

def create_parser_agsrest_servop_parent(parents):
    agsrest_servop_parent = argparse.ArgumentParser(add_help = False, parents = parents)
    agsrest_servop_parent.set_defaults(func = execute_args)

    group_req, group_opt, group_flags = create_argument_groups(agsrest_servop_parent, include_help_flag = False)

    group_req.add_argument("-n", "--name", required = True,
        help = "Name of the service.")
    group_req.add_argument("-t", "--type", choices = ["MapServer","GpServer"], required = True,
        help = "The type of the service.")

    group_opt.add_argument("-f", "--folder",
        help = "The folder that the service resides in.")

    return agsrest_servop_parent

def create_parser_agsrest_machine_parent(parents):
    agsrest_machine_parent = argparse.ArgumentParser(add_help = False, parents = parents)
    agsrest_machine_parent.set_defaults(func = execute_args)

    group_req, group_opt, group_flags = create_argument_groups(agsrest_machine_parent, include_help_flag = False)

    group_req.add_argument("-n", "--name", required = True,
        help = "Name of the machine.")

    return agsrest_machine_parent
