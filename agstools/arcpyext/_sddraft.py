from __future__ import print_function, unicode_literals, absolute_import

import argparse

from os import path
from agstools._helpers import create_argument_groups, namespace_to_dict
from agstools._storenamevaluepairs import StoreNameValuePairs
from ._helpers import config_to_settings, open_map_document

def create_parser_sddraft(parser):
    parser_sddraft = parser.add_parser("sddraft", add_help = False,
        help = "Converts a map document (*.mxd) to an ArcGIS Server service definition draft.",
        formatter_class = argparse.RawDescriptionHelpFormatter)
    parser_sddraft.set_defaults(func = _process_arguments, lib_func = mxd_to_sddraft, _json_files = ["config"])

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
corresponding to the name of properties on the arcpy.mapping.MapSDDraft class, and
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
        "anti_aliasing_mode": ("None" | "Fastest" | "Fast" | "Normal" | "Best"),
        "cluster": "clusterNameHere",
        "description": "Service description goes here.",
        "disable_identify_relates": (true | false),
        "enable_dynamic_layers": (true | false),
        "feature_server": {
            "allow_geometry_updates": (true | false),
            "allow_others_to_delete": (true | false),
            "allow_others_to_query": (true | false),
            "allow_others_to_update": (true | false),
            "allow_true_curves_updates": (true | false),
            "capabilities": [
                "Create",
                "Query",
                "Update",
                "Delete",
                "Sync"
            ],
            "enable_ownership_based_access_control": (true | false),
            "enable_z_defaults": (true | false),
            "enabled": (true | false),
            "max_record_count": 1000,
            "realm": "MyRealm",
            "z_default_value": 0.0
        },
        "high_isolation": (true | false),
        "idle_timeout": 600,
        "instances_per_container": 4,
        "keep_cache": (true | false),
        "kml_server": {
            "capabilities": [
                "SingleImage",
                "SeparateImages",
                "Vectors"
            ],
            "compatibility_mode": ("GoogleEarth" | "GoogleMaps" | "GoogleMobile"),
            "dpi": 96,
            "feature_limit": 1000,
            "image_size": 2000,
            "link_name": "FooBarService",
            "link_description": "This is a service description.",
            "message": "This is the one-time message that appears on adding the service to a client.",
            "min_refresh_period": 30,
            "use_default_snippets": (true | false),
            "use_network_link_control_tag": (true | false),
            "enabled": (true | false)
        },
        "max_instances": 4,
        "max_record_count": 1000,
        "min_instances": 1,
        "mobile_server": {
            "enabled": (true | false)
        },
        "na_server": {
            "enabled": (true | false)
        },
        "name": "ServiceNameGoesHere",
        "recycle_interval": 24,
        "recycle_start_time": "23:00",
        "replace_existing": (true | false),
        "schema_locking_enabled": (true | false),
        "schematics_server": {
            "capabilities": [
                "Query",
                "Editing"
            ],
            "enabled": (true | false)
        },
        "summary": "Map service summary goes here.",
        "text_anti_aliasing_mode": ("None" | "Normal" | "Force"),
        "usage_timeout": 60,
        "wait_timeout": 600,
        "wcs_server": {
            "abstract": "This is an example abstract.",
            "access_constraints": "This service contains sensitive business data, INTERNAL USE ONLY.",
            "address": "123 Fake St.",
            "administrative_area": "State of FooBar",
            "city": "Faketown",
            "country": "Kingdom of FooBar",
            "custom_get_capabilities": (true | false),
            "email": "email@example.com",
            "enabled": (true | false),
            "facsimile": "+111 1111 1111",
            "fees": "Service is free for non-commercial use.",
            "individual_name": "Doe",
            "keyword": "FooBar, Spatial",
            "name": "FooBarService",
            "organization": "Fake Corp.",
            "path_to_custom_get_capabilities_files": "http://foobar.com/services/Wms/FooBarRoads",
            "phone": "+222 2222 2222",
            "position_name": "WMS Services Contact Officer",
            "post_code": 10532,
            "title": "FooBar Roads Service"
        },
        "wms_server": {
            "abstract": "This is an example abstract.",
            "access_constraints": "This service contains sensitive business data, INTERNAL USE ONLY.",
            "address": "123 Fake St.",
            "administrative_area": "State of FooBar",
            "address_type": "postal",
            "capabilities": [
                "GetCapabilities",
                "GetMap",
                "GetFeatureInfo",
                "GetStyles",
                "GetLegendGraphic",
                "GetSchemaExtension"
            ],
            "city": "Faketown",
            "country": "Kingdom of FooBar",
            "custom_get_capabilities": (true | false),
            "email": "email@example.com",
            "enabled": (true | false),
            "facsimile": "+111 1111 1111",
            "fees": "Service is free for non-commercial use.",
            "inherit_layer_names": (true | false),
            "individual_name": "Doe",
            "keyword": "FooBar, Spatial",
            "name": "FooBarService",
            "organization": "Fake Corp.",
            "path_to_custom_get_capabilities_files": "http://foobar.com/services/Wms/FooBarRoads",
            "path_to_custom_sld_file": "http://foobar.com/services/FooBarRoads.sld",
            "phone": "+222 2222 2222",
            "position_name": "WMS Services Contact Officer",
            "post_code": 10532,
            "title": "FooBar Roads Service"
        },
        "wfs_server": {
            "abstract": "This is an example abstract.",
            "access_constraints": "This service contains sensitive business data, INTERNAL USE ONLY.",
            "address": "123 Fake St.",
            "administrative_area": "State of FooBar",
            "app_schema_prefix": "FooBar",
            "axis_order_wfs_10": ("LatLong" | "LongLat"),
            "axis_order_wfs_11": ("LatLong" | "LongLat"),
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
            "name": "FooBarService",
            "organization": "Fake Corp.",
            "path_to_custom_get_capabilities_files": "http://foobar.com/services/Wfs/Roads",
            "phone": "+222 2222 2222",
            "position_name": "WMS Services Contact Officer",
            "post_code": 10532,
            "provider_site": "http://www.foobar.com/",
            "service_type": "WFS",
            "service_type_version": "1.1.0",
            "title": "FooBar Roads Service"
        }
    }
}
"""

def mxd_to_sddraft(mxd, output = None, name = None, folder = None, leave_existing = False, settings = {}):
    import arcpyext

    mxd = open_map_document(mxd)

    print("Creating SD Draft for: {0}".format(mxd.filePath))

    if name == None:
        name = path.splitext(path.basename(mxd.filePath))[0].strip().replace(" ", "_")

    if output == None:
        output = "{0}.sddraft".format(path.splitext(mxd.filePath)[0])

    if not "replace_existing" in settings:
        settings["replace_existing"] = not leave_existing

    if not "keep_cache" in settings:
        settings["keep_cache"] = True

    sd_draft = arcpyext.publishing.convert_map_to_service_draft(mxd, output, name, folder)

    sd_draft._set_props_from_dict(settings)

    sd_draft.save()

    print("Done, SD Draft created at: {0}".format(output))

def _process_arguments(args):
    args, func = namespace_to_dict(args)

    args = config_to_settings(args)

    func(**args)