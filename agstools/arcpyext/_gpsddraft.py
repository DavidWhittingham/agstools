from __future__ import print_function, unicode_literals, absolute_import

import argparse
import imp
import os
import re

from agstools._helpers import create_argument_groups, namespace_to_dict, format_input_path, format_output_path, read_json_file
from agstools._storenamevaluepairs import StoreNameValuePairs
from ._helpers import config_to_settings

def create_gp_sddraft(toolbox, result, output = None, name = None, folder = None, leave_existing = False, settings = {}):
    import arcpy
    import arcpyext

    # CreateGPSDDraft function doesn't work with relative paths, so we make sure they are absolute
    toolbox = os.path.abspath(toolbox)

    print("Creating SD Draft for toolbox: {0}".format(toolbox))

    if output == None:
        output = "{0}.sddraft".format(os.path.splitext(toolbox)[0])
    else:
        output = os.path.abspath(output)

    if name == None:
        path_pair = os.path.splitext(toolbox)
        name = path_pair[0]
        name = re.sub('[^0-9a-zA-Z]+', '_', name)

    arcpy.CreateGPSDDraft(
        result, output, name, server_type = "ARCGIS_SERVER", copy_data_to_server = False, folder_name = folder)

    sd_draft = arcpyext.publishing.load_gp_sddraft(output)

    if not "replace_existing" in settings:
        settings["replace_existing"] = not leave_existing

    sd_draft._set_props_from_dict(settings)

    sd_draft.save()

    print("Done, SD Draft created at: {0}".format(output))

def create_parser_gp_sddraft(parser):
    parser_sddraft = parser.add_parser("gpsddraft", add_help = False,
        help = "Creates a service definition draft for a Geo-processing Service from an ArcGIS Toolbox.",
        description = "Creates a service definition draft for a Geo-processing Service from a (Python) Toolbox.",
        formatter_class = argparse.RawDescriptionHelpFormatter)
    parser_sddraft.set_defaults(func = _process_arguments, lib_func = create_gp_sddraft, _json_files = ["config"])

    group_req, group_opt, group_flags = create_argument_groups(parser_sddraft)

    group_req.add_argument("-t", "--toolbox", required = True,
        help = "Path to the Toolbox (*.tbx, *.pyt) to create the GP service from.")

    group_req.add_argument("-r", "--tool_runner", required = True,
        help = "Path to a Python script that executes the tool.  The script must provide the tool result on a 'RESULT' variable/getter in the script's namespace.  A tool result is required in order to build a GP service.")
    group_opt.add_argument("-o", "--output",
        help = "The path to save the SD Draft to. If left out, defaults to saving with the same filename/path as the \
            Toolbox (use '*.sddraft' as extension).")
    group_opt.add_argument("-n", "--name",
        help = "Name of the published service.  Defaults to the Toolbox name (spaces and periods in the name will \
            be replaced by underscores).")
    group_opt.add_argument("-f", "--folder",
        help = "The server folder to publish the service to.  If left out, defaults to the root directory.")
    group_opt.add_argument("-s", "--settings", default = {}, nargs = "*", action = StoreNameValuePairs,
        help = "Additional key/value settings (in the form 'key=value') that will be processed by the SD Draft creator.")
    group_opt.add_argument("-c", "--config",
        help = "The absolute or relative path to a JSON-encoded configuration file (see below).")

    group_flags.add_argument("-l", "--leave-existing", default = False, action = "store_true",
        help = "Prevents an existing service from being overwritten.")

    parser_sddraft.epilog = """
-------------------------
CONFIGURATION INFORMATION
-------------------------
The JSON-encoded configuration file contains one mandatory key,
'serviceSettings', which provides a mechanism for passing in all service
settings into the Service Definition Draft generation process via a single
file.

Service Settings
---------------------
The 'serviceSettings' key contains a dictionary of key/value pairs with keys
corresponding to the name of properties on the arcpy.publishing.GPSDDraft
class, and values being the data that will be applied to each property on the
class.  All values are optional, but any supplied value will supersede any value
provided by one of the command-line parameters.

Example
-------
In the below example, options that require a detailed explanation are inside
parentheses.  The parentheses should not included in the configuration, only
one of the suggested values, or data as pertaining to the explanation.

Items in square brackets indicate a list is required input.  All available
options for the list will be shown.  Any combination of the listed options
may be used, but the value must be a square-bracket array containing zero or
more options.

All options are case sensitive.

For more information on each of the settings, see the ImageSDDraft class.

{
    "serviceSettings": {
        "capabilities": ["Uploads"],
        "cluster": "clusterNameHere",
        "description": "Service description goes here.",
        "execution_type": ("Synchronous" | "Asynchronous"),
        "folder": "ExampleServices",
        "high_isolation": (true | false),
        "idle_timeout": 600,
        "instances_per_container": 4,
        "max_instances": 4,
        "max_record_count": 1000,
        "min_instances": 1,
        "name": "ServiceNameGoesHere",
        "recycle_interval": 24,
        "recycle_start_time": "23:00",
        "replace_existing": (true | false),
        "result_map_server": (true | false),
        "summary": "Map service summary goes here.",
        "show_messages": ("None" | "Error" | "Warning" | "Info"),
        "usage_timeout": 60,
        "wait_timeout": 600,
        "wps_server": {
            "abstract": "This is an example abstract.",
            "access_constraints": "This service contains sensitive business data, INTERNAL USE ONLY.",
            "address": "123 Fake St.",
            "administrative_area": "State of FooBar",
            "app_schema_prefix": "FooBar",
            "city": "Faketown",
            "contact_instructions": "Contact hours are 8am-6pm, UTC.",
            "country": "Kingdom of FooBar",
            "custom_get_capabilities": (true | false),
            "email": "email@example.com",
            "enable_transactions": (true | false),
            "enabled": (true | false),
            "facsimile": "+111 1111 1111",
            "fees": "Service is free for non-commercial use.",
            "hours_of_service": "Service operates 24/7.",
            "individual_name": "Doe",
            "keyword": "FooBar, Spatial",
            "keywords_type": "Type Info",
            "name": "FooBarService",
            "organization": "Fake Corp.",
            "path_to_custom_get_capabilities_files": "http://foobar.com/services/Wfs/Roads",
            "phone": "+222 2222 2222",
            "position_name": "WMS Services Contact Officer",
            "post_code": 10532,
            "profile": "WPS profile",
            "provider_site": "http://www.foobar.com/",
            "role": "role info",
            "service_type": "WPS",
            "service_type_version": "1.1.0",
            "title": "FooBar Roads Service"
        }
    }
}
"""

def get_tool_runner_result(tool_runner_path):
    tool_runner_full_path = os.path.abspath(tool_runner_path)
    tool_runner_working_dir = os.path.dirname(tool_runner_full_path)
    orig_working_dir = os.getcwd()

    # Python tool runner will probably use relative imports
    # Working directory may not be the same though, so set working directory to compensate
    os.chdir(tool_runner_working_dir)

    try:
        # Turn tool runner script into result argument
        tool_runner = imp.load_source("gptoolrunner", tool_runner_full_path)
        return tool_runner.RESULT
    finally:
        # Set working directory back to original, for consistency
        os.chdir(orig_working_dir)

def _process_arguments(args):
    args, func = namespace_to_dict(args)

    args["result"] = get_tool_runner_result(args["tool_runner"])
    args.pop("tool_runner")

    args = config_to_settings(args)

    func(**args)