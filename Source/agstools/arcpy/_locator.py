from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow,
                      range, round, str, super, zip)

import argparse
import os

from agstools._helpers import create_argument_groups, namespace_to_dict

def create_address_locator(in_address_locator_style, in_reference_data, in_field_map, out_address_locator,
                           config_keyword = None, enable_suggestions = "DISABLED", workspace = None):
    import arcpy

    if workspace != None:
        arcpy.env.workspace = os.path.abspath(workspace)

    print("Creating locator...")
    arcpy.CreateAddressLocator_geocoding(in_address_locator_style, in_reference_data, in_field_map,
                                         out_address_locator, config_keyword, enable_suggestions)
    print("Done.")

def rebuild_address_locator(locator):
    import arcpy

    locator = os.path.abspath(locator)

    print("Rebuilding locator: {0}".format(locator))
    arcpy.RebuildAddressLocator_geocoding(locator)
    print("Done.")

def create_parser_makeloc(parser):
    parser_makeloc = parser.add_parser("makeloc", add_help = False,
        help = "Creates an Address Locator from a configuration file.",
        formatter_class = argparse.RawDescriptionHelpFormatter)
    parser_makeloc.set_defaults(func = _process_makeloc_arguments, lib_func = create_address_locator, _json_files = ["config"])

    group_req, group_opt, group_flags = create_argument_groups(parser_makeloc)

    group_req.add_argument("-c", "--config", required = True,
        help = "The absolute or relative path to a JSON-encoded configuration file (see below).")

    group_opt.add_argument("--workspace",
        help = "The absolute or relative path to a workspace containing data for the locator.  Can be used so that \
            connection details do not have to be supplied in the configuration for input reference data.")

    parser_makeloc.epilog = """
-------------------------
CONFIGURATION INFORMATION
-------------------------
The JSON-encoded configuration file contains four mandatory keys,
'in_address_locator_style', 'in_reference_data', 'in_field_map', and
'out_address_locator'.  There are also two optional keys, 'config_keyword' and
'enable_suggestions'.  These six keys (and there values) correspond directly
to the input fields for the 'Create Address Locator' toolbox.  See the ArcGIS
Desktop help for more information."""

def create_parser_rebuildloc(parser):
    parser_rebuildloc = parser.add_parser("rebuildloc", add_help = False,
        help = "Rebuilds an Address Locator.",
        formatter_class = argparse.RawDescriptionHelpFormatter)
    parser_rebuildloc.set_defaults(func = _process_rebuildloc_arguments, lib_func = rebuild_address_locator, _json_files = ["config"])

    group_req, group_opt, group_flags = create_argument_groups(parser_rebuildloc)
    group_mut_exc = parser_rebuildloc.add_mutually_exclusive_group(required = True)

    # next line doesn't change the help output currently, hopefully bug will be fixed in argparse in the future
    group_mut_exc.title = "optional arguments (at least one required)"

    group_mut_exc.add_argument("-l", "--locator",
        help = "The absolute or relative path to an Address Locator.")

    group_mut_exc.add_argument("-c", "--config",
        help = "The absolute or relative path to a JSON-encoded configuration file (see below).")

    parser_rebuildloc.epilog = """
-------------------------
CONFIGURATION INFORMATION
-------------------------
The JSON-encoded configuration file contains one mandatory key,
'out_address_locator'.  This key (and it's values) corresponds directly
to the 'out_address_locator' input field for the 'Create Address Locator'
toolbox.  See the ArcGIS Desktop help for more information on this tool.

This allows for the configuration file that built the locator to be re-used
in rebuilding it.
"""

def _process_rebuildloc_arguments(args):
    if args.config != None:
        config_path_dir = os.path.dirname(os.path.abspath(vars(args)["config"]))
        cwd = os.getcwd()

        args, func = namespace_to_dict(args)

        os.chdir(config_path_dir)
        func(args["config"]["out_address_locator"])
        os.chdir(cwd)
    else:
        args, func = namespace_to_dict(args)
        args.pop("config", None)
        func(**args)

def _process_makeloc_arguments(args):
    config_path_dir = os.path.dirname(os.path.abspath(vars(args)["config"]))
    cwd = os.getcwd()

    args, func = namespace_to_dict(args)

    args = args["config"]

    # "in_reference_data" can optionally be a JSON-encoded descriptor
    # convert the descriptor to the text format expected by the arcpy function
    if not isinstance(args["in_reference_data"], basestring):
        args["in_reference_data"] = ";".join(
            ["'{0}' '{1}'".format(v["reference_data"], v["role"]) for v in args["in_reference_data"]])

    # "in_field_map" can optionally be a JSON-encoded descriptor
    # convert the descriptor to the text format expected by the arcpy function
    if not isinstance(args["in_field_map"], basestring):
        args["in_field_map"] = ";".join(
            ["'{0}' '{1}'  VISIBLE NONE".format(
                v["locator_field_alias"], "" if v["dataset_field_name"] is None else v["dataset_field_name"])
                    for v in args["in_field_map"]])

    os.chdir(config_path_dir)
    func(**args)
    os.chdir(cwd)