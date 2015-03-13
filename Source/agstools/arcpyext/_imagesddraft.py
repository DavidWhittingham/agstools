from __future__ import print_function, unicode_literals, absolute_import

import argparse
import re

from os import path

from agstools._helpers import create_argument_groups, namespace_to_dict
from agstools._storenamevaluepairs import StoreNameValuePairs

def create_image_sddraft(input, output, name = None, folder = None, leave_existing = False, settings = {}):
    import arcpy
    import arcpyext

    input = path.abspath(input)
    output = path.abspath(output)

    if name == None:
        path_pair = path.splitext(input)
        if path_pair[1].lower() == ".lyr":
            name = path_pair[0]
        else:
            name = path.basename(input)

        name = re.sub('[^0-9a-zA-Z]+', '_', name)

    if not "replace_existing" in settings:
        settings["replace_existing"] = not leave_existing

    if not "keep_cache" in settings:
        settings["keep_cache"] = True

    arcpy.CreateImageSDDraft(input, output, name, folder_name = folder, server_type = "ARCGIS_SERVER")

    sd_draft = arcpyext.mapping.ImageSDDraft(output)

    def set_arg(sd_draft, k, v):
        if hasattr(sd_draft, k):
            setattr(sd_draft, k, v)

    # min instances must be set before max instances, so we get it out of the way
    if "min_instances" in settings:
        set_arg(sd_draft, "min_instances", settings["min_instances"])
        del settings["min_instances"]

    for k, v in settings.items():
        set_arg(sd_draft, k, v)

    sd_draft.save()

    print("Done, SD Draft created at: {0}".format(output))

def create_parser_image_sddraft(parser):
    parser_sddraft = parser.add_parser("imagesddraft", add_help = False,
        help = "Creates a service definition draft for an Image Service from a raster layer.",
        description = "Creates a service definition draft for an Image Service from a raster layer.\n\n" +
            "One of the two arguments from the first optional set below must be provided.",
        formatter_class = argparse.RawDescriptionHelpFormatter)
    parser_sddraft.set_defaults(func = _process_arguments, lib_func = create_image_sddraft, _json_files = ["config", "json_path"])

    group_req, group_opt, group_flags = create_argument_groups(parser_sddraft)
    group_mut_exc = parser_sddraft.add_mutually_exclusive_group(required = True)

    # next line doesn't change the help output currently, hopefully bug will be fixed in argparse in the future
    group_mut_exc.title = "optional arguments (at least one required)"

    group_mut_exc.add_argument("-i", "--input",
        help = "Path to raster layer to create the image service from.")

    group_mut_exc.add_argument("-j", "--json-path",
        help = "Path to JSON-encoded file with a 'dataSource' field containing the raster path.")

    group_req.add_argument("-o", "--output", required = True,
        help = "The path to save the SD Draft to. If left out, defaults to saving with the same filename/path as the \
            MXD (use '*.sddraft' as extension).")

    group_opt.add_argument("-n", "--name",
        help = "Name of the published service.  Defaults to the raster layer name (spaces and periods in the name will \
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
corresponding to the name of properties on the arcpy.mapping.ImageSDDraft
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
        "allowed_compressions": ["None", "JPEG", "LZ77", "LERC"],
        "allowed_mosaic_methods": [
            "NorthWest",
            "Center",
            "LockRaster",
            "ByAttribute",
            "Nadir",
            "Viewpoint",
            "Seamline",
            "None"
        ],
        "available_fields": (This is a list of available fields from the data source),
        "cluster": "clusterNameHere",
        "default_resampling_method": (This is one of the following integers:
            0 - nearest neighbour,
            1 - bilinear,
            2 - cubic,
            3 - majority
        ),
        "description": "Service description goes here.",
        "enabled_extensions": [
            "WMSServer",
            "WCSServer",
            "JPIPServer"
        ],
        "high_isolation": (true | false),
        "idle_timeout": 600,
        "instances_per_container": 4,
        "keep_cache": true,
        "max_download_image_count": 20,
        "max_download_size_limit": 2048,
        "max_image_height": 4100,
        "max_image_width": 15000,
        "max_instances": 4,
        "max_mosaic_image_count": 20,
        "max_record_count": 1000,
        "min_instances": 1,
        "name": "ServiceNameGoesHere",
        "recycle_interval": 24,
        "recycle_start_time": "23:00",
        "replace_existing": true,
        "return_jpgpng_as_jpg": (true | false),
        "summary": "Map service summary goes here.",
        "usage_timeout": 60,
        "wait_timeout": 600
    }
}
"""

def _process_arguments(args):
    args, func = namespace_to_dict(args)

    if "json_path" in args:
        if args["json_path"] != None:
            args["input"] = args["json_path"]["dataSource"]
        args.pop("json_path", None)

    if "config" in args:
        if args["config"] != None:
            if "settings" in args and args["settings"] != None:
                args["settings"].update(args["config"]["serviceSettings"])
            else:
                args["settings"] = args["config"]["serviceSettings"]
        args.pop("config", None)

    func(**args)