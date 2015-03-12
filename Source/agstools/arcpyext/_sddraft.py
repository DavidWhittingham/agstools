import argparse

from os import path
from agstools._helpers import create_argument_groups, namespace_to_dict
from agstools._storenamevaluepairs import StoreNameValuePairs
from ._mxd_helpers import open_map_document

def mxd_to_sddraft(mxd, output = None, name = None, folder = None, leave_existing = False, settings = {}):
    import arcpyext

    mxd = open_map_document(mxd)

    if name == None:
        name = path.splitext(path.basename(mxd.filePath))[0].strip().replace(" ", "_")

    if output == None:
        output = "{0}.sddraft".format(path.splitext(mxd.filePath)[0])

    if not "replace_existing" in settings:
        settings["replace_existing"] = not leave_existing

    if not "keep_cache" in settings:
        settings["keep_cache"] = True

    sd_draft = arcpyext.mapping.convert_map_to_service_draft(mxd, output, name, folder)

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

def create_parser_sddraft(parser):
    parser_sddraft = parser.add_parser("sddraft", add_help = False,
        help = "Converts a map document (*.mxd) to an ArcGIS Server service definition draft.",
        formatter_class = argparse.RawDescriptionHelpFormatter)
    parser_sddraft.set_defaults(func = _mxd_to_sddraft, lib_func = mxd_to_sddraft, _json_files = ["config"])

    group_req, group_opt, group_flags = create_argument_groups(parser_sddraft)

    group_req.add_argument("-m", "--mxd", required = True,
        help = "Path to the map document to be converted.")

    group_opt.add_argument("-n", "--name",
        help = "Name of the published service.  Defaults to the map document file name (spaces in the file name will \
            be replaced by underscores).")
    group_opt.add_argument("-o", "--output",
        help = "The path to save the SD Draft to. If left out, defaults to saving with the same filename/path as the \
            MXD (use '*.sddraft' as extension).")
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
corresponding to the name of properties on the arcpy.mapping.SDDraft class, and
values being the data that will be applied to each property on the class.  All
values are optional, but any supplied value will supersede any value provided
by one of the command-line parameters.

Example
-------
In the below example, options that have more than one valid option are enclosed
in parentheses and separated by the pipe symbol.

For the "enabled_extensions" and "feature_access_enabled_operations"
parameters, any combination of the listed options may be used, but the value
must be an array containing zero or more options.  All options are case
sensitive.

For more information on each of the settings, see the SDDraft class.

{
    "serviceSettings": {
        "anti_aliasing_mode": ("None | "Fastest" | "Fast" | "Normal" | "Best"),
        "cluster": "clusterNameHere",
        "description": "Service description goes here.",
        "disable_identify_relates": (true | false),
        "enable_dynamic_layers": (true | false),
        "enabled_extensions": [
            "FeatureServer",
            "MobileServer",
            "WMSServer",
            "KmlServer",
            "NAServer",
            "WFSServer",
            "WCSServer",
            "SchematicsServer"
        ],
        "feature_access_enabled_operations": [
            "Create",
            "Query",
            "Update",
            "Delete",
            "Sync"
        ],
        "high_isolation": (true | false),
        "idle_timeout": 600,
        "instances_per_container": 4,
        "keep_cache": true,
        "max_instances": 4,
        "max_record_count": 1000,
        "min_instances": 1,
        "name": "ServiceNameGoesHere",
        "recycle_interval": 24,
        "recycle_start_time": "23:00",
        "replace_existing": true,
        "schema_locking_enabled": (true | false),
        "summary": "Map service summary goes here.",
        "text_anti_aliasing_mode": ("None" | "Normal" | "Force"),
        "usage_timeout": 60,
        "wait_timeout": 600
    }
}
"""

def _mxd_to_sddraft(args):
    args, func = namespace_to_dict(args)

    if "config" in args:
        if args["config"] != None:
            if "settings" in args and args["settings"] != None:
                args["settings"].update(args["config"]["serviceSettings"])
            else:
                args["settings"] = args["config"]["serviceSettings"]
        args.pop("config", None)

    func(**args)