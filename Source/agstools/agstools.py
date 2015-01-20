from ast import literal_eval
from datetime import timedelta
from json import load
from os import path, remove, makedirs, listdir
from shutil import copy2, move, rmtree
import argparse
import imp
import fnmatch
import sys
import tempfile
import time

ARCPYEXT_AVAILABLE = True
AGSADMIN_AVAILABLE = True

try:
    imp.find_module("arcpyext")
except ImportError:
    ARCPYEXT_AVAILABLE = False

try:
    imp.find_module("agsadmin")
except ImportError:
    AGSADMIN_AVAILABLE = False

REQUIRED_PARAMS_TEXT = "required arguments"
OPTIONAL_PARAMS_TEXT = "optional arguments"
FLAGS_TEXT = "optional flags"
HELP_FLAG_TEXT = "Show this help message and exit."
MXD_FILETYPE_PATH_FILTER = "*.mxd"

DATA_SOURCE_TEMPLATES_HELP = """
-------------------------
CONFIGURATION INFORMATION
-------------------------
The JSON-encoded configuration file contains one mandatory key,
'dataSourceTemplates', which provides a mechanism for replacing layer data
sources using templates.

Data Source Templates
---------------------
The 'dataSourceTemplates' key contains an array of objects, with each one
taking the form of a dictionary containing two keys, "matchCriteria" and
"dataSource", both of which are also dictionaries.

Match criteria is a dictionary of key/value pairs that are compared to the
details of layers/table views.  If all listed match criteria are contained in
the layer/table view details, the template is a match and the date source
described in the "dataSource" key will be used to replace the table/layer
views data source.  Valid match keys for layers are 'name', 'longName',
'datasetName', 'dataSource', 'serviceType', 'userName', 'server', 'service',
and 'database'.  Valid match keys for table views are 'datasetName',
'dataSource', 'definitionQuery', and 'workspacePath'.  String values are
case sensitive.

Data source describes the replacement data source for a layer. As a minimum,
it should provide a "workspacePath" key that is the path (relative or absolute
to executing path) to a valid Arc workspace.  Optionally, the data source
dictionary also supports 'datasetName', 'workspaceType', and 'schema' keys,
allowing you to change these data source properties simultaneously.

Example
-------
{
    "dataSourceTemplates": [
        {
            "matchCriteria": {
                "server": "foo.server.local",
                "userName": "bar"
            },
            "dataSource": {
                "workspacePath": "./path/to/conn.sde"
            }
        }
    ]
}
"""


class StoreNameValuePairs(argparse.Action):
    """Simple argparse Action class for taking multiple string values in the form a=b and returning a dictionary.
    Literal values (i.e. booleans, numbers) will be converted to there appropriate Python types.
    On either side of the equals sign, double quotes can be used to contain a string that includes white space."""

    def __call__(self, parser, namespace, values, option_string = None):
        values_dict = {}
        for pair in values:
            k, v = pair.split("=")
            try:
                v = literal_eval(v)
            except SyntaxError:
                pass

            values_dict[k] = v

        setattr(namespace, self.dest, values_dict)

def delete_service(restadmin, name, type, folder):
    print("Deleting service...")
    restadmin.delete_service(name, type, folder)
    print("Service deleted.")

def mxd_to_sddraft(mxd, output = None, name = None, folder = None, leave_existing = False, settings = {}):
    import arcpy
    import arcpyext

    mxd = _open_map_document(mxd)

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

def publish_sd(sd, conn):
    import arcpy

    sd = _format_input_path(sd, "Path to the service definition is invalid.")
    conn = _format_input_path(conn, "Path to ArcGIS Server Connection file is invalid.")

    print("Publishing service definition...")

    arcpy.UploadServiceDefinition_server(sd, conn)

    print("Done, service definition published.")

def save_a_copy(mxd, output_path, version = None):
    import arcpy

    mxd = _open_map_document(mxd)

    output_path = _format_output_path(output_path)

    print("Opening map document: {0}".format(mxd))
    map = arcpy.mapping.MapDocument(mxd)

    print("Saving a copy to: {0}".format(output_path))
    if version == None:
        map.saveACopy(output_path)
    else:
        map.saveACopy(output_path, version)

    print("Done.")

def sddraft_to_sd(sddraft, output = None, persist = False):
    import arcpyext

    print("Creating service definition from draft...")

    sddraft = _format_input_path(sddraft, "Path to service definition draft is invalid.")

    if output == None:
        output = "{0}.sd".format(path.splitext(sddraft)[0])
    else:
        output = _format_output_path(output)

    if persist == True:
        sd_draft_backup_path = "{0}.sddraft.bak".format(path.splitext(sddraft)[0])
        copy2(sddraft, sd_draft_backup_path)

    sd_draft = arcpyext.mapping.SDDraft(sddraft)

    arcpyext.mapping.convert_service_draft_to_staged_service(sd_draft, output)

    if persist == True:
        move(sd_draft_backup_path, sddraft)

    print("Done, service definition created at: {0}".format(output))

def update_data(mxd, config, output_path = None, reload_symbology = False):
    import arcpy
    import arcpyext

    mxd = _open_map_document(mxd)
    working_folder = path.join(tempfile.gettempdir(), "agstools")
    symbology_path = path.join(working_folder, "symbology")

    if (reload_symbology):
        if path.exists(symbology_path):
            rmtree(symbology_path)
        _save_layers(mxd, symbology_path)

    print("Listing data sources for replacement...")
    lds = arcpyext.mapping.list_document_data_sources(mxd)
    rdsl = arcpyext.mapping.create_replacement_data_sources_list(lds, config["dataSourceTemplates"])

    print("Updating data sources...")
    arcpyext.mapping.change_data_sources(mxd, rdsl)

    if (reload_symbology):
        _load_symbology_from_layers(mxd, symbology_path)
        rmtree(symbology_path)

    print("Saving map document...")
    if output_path != None:
        output_path = _format_output_path(output_path)
        if path.exists(output_path):
            remove(output_path)

        mxd.saveACopy(output_path)
    else:
        mxd.save()

    if path.exists(working_folder):
        rmtree(working_folder)

    print("Done.")

def update_data_folder(input_path, output_path, config, reload_symbology = False):
    import arcpy
    import arcpyext

    mxd_list = _filter_uptodate_mxds(input_path, output_path)

    for mxd_in in mxd_list:
        mxd_out = _format_output_path(path.join(output_path, mxd_in))
        mxd_in = path.join(input_path, mxd_in)

        update_data(mxd_in, config, mxd_out, reload_symbology)

def start_service(restadmin, name, type, folder):
    serv = restadmin.get_service(name, type, folder)

    print("Starting service...")
    serv.start_service()
    print("Service started.")

def stop_service(restadmin, name, type, folder):
    serv = restadmin.get_service(name, type, folder)

    print("Stopping service...")
    serv.stop_service()
    print("Service stopped.")

def _compare_last_modified(base_file, other_file):
    return path.getmtime(other_file) - path.getmtime(base_file)

def _create_argument_groups(parser, req_group = True, opt_group = True, flags_group = True, include_help_flag = True):
    """Creates three argument groups for use by all sub-parsers, the required group, the optional group, and the
    flags/switches group.  These are returned as a tuple in the above listed order. The function parameters allow you
    to specify exactly which groups you would like created, with None being returned for any group that isn't
    created."""

    req = parser.add_argument_group(REQUIRED_PARAMS_TEXT) if req_group else None
    opt = parser.add_argument_group(OPTIONAL_PARAMS_TEXT) if opt_group else None

    if flags_group:
        flags = parser.add_argument_group(FLAGS_TEXT)
        if include_help_flag:
            flags.add_argument("-h", "--help", action = "help", help = HELP_FLAG_TEXT)
    else:
        flags = None

    return (req, opt, flags)

def _create_output_path(output_path):
    """Creates the directory structure for a given path if it does not already exist."""
    if not path.exists(output_path):
        makedirs(output_path)

def _create_parser_agsrest_parent():
    parser_agsrest_parent = argparse.ArgumentParser(add_help = False)
    parser_agsrest_parent.set_defaults(
        parse_for_restadmin = True,
        utc_delta = time.timezone / -60 if time.daylight == 0 else time.altzone / -60,
        instance = 'arcgis',
        port = 6080
    )

    group_req, group_opt, group_flags = _create_argument_groups(parser_agsrest_parent, include_help_flag = False)
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

def _create_parser_agsrest_servop_parent(parents):
    agsrest_servop_parent = argparse.ArgumentParser(add_help = False, parents = parents)
    agsrest_servop_parent.set_defaults(func = _execute_args, lib_func = start_service)

    group_req, group_opt, group_flags = _create_argument_groups(agsrest_servop_parent)

    group_req.add_argument("-n", "--name", required = True,
        help = "Name of the service.")
    group_req.add_argument("-t", "--type", choices = ["MapServer"], required = True,
        help = "The type of the service.")

    group_opt.add_argument("-f", "--folder",
        help = "The folder that the service resides in.")

    return agsrest_servop_parent

def _create_parser_save_copy(parser):
    parser_copy = parser.add_parser("copy", add_help = False,
        help = "Saves a copy of an ArcGIS map document, optionally in a different output version.")
    parser_copy.set_defaults(func = _execute_args, lib_func = save_a_copy)

    group_req, group_opt, group_flags = _create_argument_groups(parser_copy)

    group_req.add_argument("-m", "--mxd", required = True,
        help = "File path to the map document (*.mxd) to copy.")

    group_req.add_argument("-o", "--output", required = True,
        help = "The path on which to save the copy of the map document.")

    group_opt.add_argument("-v", "--version", type=str, choices=["8.3", "9.0", "9.2", "9.3", "10.0", "10.1", "10.3"],
        help = "The output version number for the saved copy.")

def _create_parser_delete(parser, parents):
    """Creates a sub-parser for deleting an ArcGIS Server Service."""

    parser_delete = parser.add_parser("delete", parents = parents, add_help = False,
        help = "Deletes a service on an ArcGIS Server instance.")
    parser_delete.set_defaults(func = _execute_args, lib_func = delete_service)

def _create_parser_publish(parser):
    parser_publish = parser.add_parser("publish", add_help = False,
        help = "Publishes a service definition to an ArcGIS Server instance.")
    parser_publish.set_defaults(func = _execute_args, lib_func = publish_sd)

    group_req, group_opt, group_flags = _create_argument_groups(parser_publish, opt_group = False)

    group_req.add_argument("-s", "--sd", required = True,
        help = "File path to the service definition (*.sd) to publish.")
    group_req.add_argument("-c", "--conn", required = True,
        help = "File path to the ArcGIS Server Connection File (*.ags) for the server to publish the file to.")

def _create_parser_sd(parser):
    parser_sd = parser.add_parser("sd", add_help = False,
        help = "Stages an ArcGIS Server service definition draft into a service definition ready for publishing (this \
            will by default delete the draft).")
    parser_sd.set_defaults(func = _execute_args, lib_func = sddraft_to_sd)

    group_req, group_opt, group_flags = _create_argument_groups(parser_sd)

    group_req.add_argument("-s", "--sddraft", required = True,
        help = "File path to the service definition draft (*.sddraft) to finalize.")

    group_opt.add_argument("-o", "--output", required = False,
        help = "The path on which to save the staged service definition. If left out, defaults to saving with the \
            same filename/path as the draft (use '*.sd' as extension).")

    group_flags.add_argument("-p", "--persist", default = False, action = "store_true",
        help = "After staging the Service Defintion, re-save the draft in it's original location")

def _create_parser_sddraft(parser):
    parser_sddraft = parser.add_parser("sddraft", add_help = False,
        help = "Converts a map document (*.mxd) to an ArcGIS Server service definition draft.",
        formatter_class = argparse.RawDescriptionHelpFormatter)
    parser_sddraft.set_defaults(func = _mxd_to_sddraft, lib_func = mxd_to_sddraft, _json_files = ["config"])

    group_req, group_opt, group_flags = _create_argument_groups(parser_sddraft)

    group_req.add_argument("-m", "--mxd", required = True,
        help = "Path to the map document to be converted.")

    group_opt.add_argument("-n", "--name", required = False,
        help = "Name of the published service.  Defaults to the map document file name (spaces in the file name will \
            be replaced by underscores).")
    group_opt.add_argument("-o", "--output", required = False,
        help = "The path to save the SD Draft to. If left out, defaults to saving with the same filename/path as the \
            MXD (use '*.sddraft' as extension).")
    group_opt.add_argument("-f", "--folder", required = False,
        help = "The server folder to publish the service to.  If left out, defaults to the root directory.")
    group_opt.add_argument("-s", "--settings", default = {}, required = False, nargs = "*", action = StoreNameValuePairs,
        help = "Additional key/value settings (in the form 'key=value') that will be processed by the SD Draft creator.")
    group_req.add_argument("-c", "--config",
        help = "The absolute or relative path to the JSON-encoded configuration data (see below).")

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

def _create_parser_start(parser, parents):
    parser_start = parser.add_parser("start", parents = parents, add_help = False,
        help = "Starts a service on an ArcGIS Server instance.")
    parser_start.set_defaults(func = _execute_args, lib_func = start_service)

def _create_parser_stop(parser, parents):
    parser_stop = parser.add_parser("stop", parents = parents, add_help = False,
        help = "Stops a service on an ArcGIS Server instance.")
    parser_stop.set_defaults(func = _execute_args, lib_func = stop_service)

def _create_parser_update_data(parser):
    """Creates a sub-parser for updating the data sources of a map document."""

    parser_update_data = parser.add_parser("updatedata", add_help = False,
        help = "Updates the workspace (data source) of each layer in a map document.",
        formatter_class = argparse.RawDescriptionHelpFormatter)
    parser_update_data.set_defaults(func = _update_data, lib_func = update_data)

    group_req, group_opt, group_flags = _create_argument_groups(parser_update_data)

    group_req.add_argument("-m", "--mxd", required = True,
        help = "The map document to be updated.")
    group_req.add_argument("-c", "--config",
        help = "The absolute or relative path to the JSON-encoded configuration data (see below).")

    group_opt.add_argument("-o", "--output-path",
        help = "The path to a location you would like the map document saved to, \
            in the event that you do not wish to overwrite the original.")

    group_flags.add_argument("-r", "--reload-symbology", action = "store_true",
        help = "Forces the output MXD to have its symbology set based on the input MXD (ArcMap will drop symbology if the underlying data source is even slightly different).")

    parser_update_data.epilog = DATA_SOURCE_TEMPLATES_HELP

def _create_parser_multi_update_data(parser):
    """Creates a sub-parser for updating the data sources of a map document."""

    help_info = "Updates the workspace (data source) of each layer in a map document, for every map document within a given folder."

    parser_update_data = parser.add_parser("multiupdatedata", add_help = False,
        help = help_info, description = help_info,
        formatter_class = argparse.RawDescriptionHelpFormatter)
    parser_update_data.set_defaults(func = _update_data_folder, lib_func = update_data_folder)

    group_req, group_opt, group_flags = _create_argument_groups(parser_update_data)

    group_req.add_argument("-i", "--input-path",
        help = "The absolute or relative path to the directory containing all MXDs to be updated.")

    group_req.add_argument("-o", "--output-path",
        help = "The absolute or relative path to the directory to output MXDs to.")

    group_req.add_argument("-c", "--config",
        help = "The absolute or relative path to the JSON-encoded configuration data (see below).")

    group_flags.add_argument("-r", "--reload-symbology", action = "store_true",
        help = "Forces the output MXD to have its symbology set based on the input MXD (ArcMap will drop symbology if the underlying data source is even slightly different).")

    parser_update_data.epilog = DATA_SOURCE_TEMPLATES_HELP

def _create_rest_admin_service(server, username, password, instance, port, utc_delta, proxy, ssl):
    import agsadmin

    if not proxy == None:
        proxy = {"http": proxy, "https": proxy}

    return agsadmin.RestAdmin(server, username, password, instance_name = instance, utc_delta = timedelta(minutes = utc_delta),
        proxies = proxy, port = port, use_ssl = ssl)

def _execute_args(args):
    args, func = _namespace_to_dict(args)
    func(**args)

def _filter_uptodate_mxds(input_path, output_path):
    """Compares the modified timestamps of MXDs in one folder to MXDs in another and returns a list of MXDs from the
    input path that are more recent then those on the output path."""
    mxd_list = _get_file_list(input_path, MXD_FILETYPE_PATH_FILTER)

    return [filename for filename in mxd_list if (
        not path.exists(path.join(output_path, filename)) or
        (_compare_last_modified(path.join(input_path, filename), path.join(output_path, filename)) < 0))
    ]

def _format_input_path(filepath, message = None):
    if not path.exists(filepath):
        raise IOError(message)
    else:
        return path.abspath(filepath)

def _format_output_path(filepath):
    filepath = path.abspath(filepath)

    dir = path.dirname(filepath)
    if not path.exists(dir):
        makedirs(dir)

    return filepath

def _get_file_list(dir_path, path_filter):
    dir_path = _format_input_path(dir_path, "MXD Directory does not exist or could not be found.")
    path_list = []

    def _list_files_in_dir(dir):
        for f in fnmatch.filter(filter(path.isfile, [path.join(dir, f) for f in listdir(dir)]), path_filter):
            path_list.append(path.relpath(f, dir_path))

    _list_files_in_dir(dir_path)
    sub_dir_list = filter(path.isdir, [path.join(dir_path, sd) for sd in listdir(dir_path)])

    for sub_dir in sub_dir_list:
        _list_files_in_dir(sub_dir)

    return path_list

def _load_symbology_from_layers(mxd, layer_path):
    import arcpy

    layers = [[layer for layer in arcpy.mapping.ListLayers(df)] for df in arcpy.mapping.ListDataFrames(mxd)]

    for (df_no, layers_in_df) in enumerate(layers):
        df_path = path.join(layer_path, str(df_no))
        df = arcpy.mapping.ListDataFrames(mxd)[df_no]

        for (layer_no, layer) in enumerate(layers_in_df):
            layer_input_path = path.join(df_path, str(layer_no) + ".lyr")
            source_layer = arcpy.mapping.Layer(layer_input_path)
            arcpy.mapping.UpdateLayer(df, layer, source_layer, True)
            
def _mxd_to_sddraft(args):
    args, func = _namespace_to_dict(args)
    
    if "config" in args and args["config"] != None:
        if "settings" in args and args["settings"] != None:
            args["settings"].update(args["config"]["serviceSettings"])
        else:
            args["settings"] = args["config"]["serviceSettings"]
        args.pop("config", None)
    
    func(**args)

def _namespace_to_dict(args):
    keys_to_remove = ("lib_func", "func", "server", "username", "password", "instance", "port", "utc_delta", "proxy",
                      "ssl", "parse_for_restadmin", "_json_files")

    args = vars(args)
    func = args["lib_func"]

    if "_json_files" in args and args["_json_files"]:
        for prop_name in args["_json_files"]:
            if args[prop_name] == None:
                continue
            args[prop_name] = _read_json_file(args[prop_name])

    if "parse_for_restadmin" in args and args["parse_for_restadmin"]:
        restadmin = _create_rest_admin_service(
            args["server"],
            args["username"],
            args["password"],
            args["instance"],
            args["port"],
            args["utc_delta"],
            args["proxy"],
            args["ssl"]
        )
        args["restadmin"] = restadmin

    for key in keys_to_remove:
        args.pop(key, None)
    return (args, func)

def _nomalize_paths_in_config(config):
    if config.has_key("dataSourceTemplates"):
        for template in config["dataSourceTemplates"]:
            if template["dataSource"].has_key("workspacePath"):
                try:
                    template["dataSource"]["workspacePath"] = _format_input_path(template["dataSource"]["workspacePath"])
                except IOError:
                    print("Could not find full path for workspace path '{0}' in '{1}' config.".format(
                        template["dataSource"]["workspacePath"], environment))
    return config

def _open_map_document(mxd):
    import arcpy
    if type(mxd) is str:
        mxd = arcpy.mapping.MapDocument(_format_input_path(mxd))
    return mxd

def _read_json_file(file_path):
    file_path = _format_input_path(file_path, "Path to the JSON-encoded data sources file is invalid.")

    with open(file_path, "r") as data_file:
        return load(data_file)

def _save_layers(mxd, output_path):
    import arcpy

    layers = [[layer for layer in arcpy.mapping.ListLayers(df)] for df in arcpy.mapping.ListDataFrames(mxd)]

    for (df_no, df) in enumerate(layers):
        df_path = path.join(output_path, str(df_no))

        for (layer_no, layer) in enumerate(df):
            layer_output_path = _format_output_path(path.join(df_path, str(layer_no) + ".lyr"))
            layer.saveACopy (layer_output_path)
            
def _update_data(args):
    args, func = _namespace_to_dict(args)

    with open(args["config"], "r") as data_file:
        args["config"] = _nomalize_paths_in_config(load(data_file))
        
    func(**args)

def _update_data_folder(args):
    args, func = _namespace_to_dict(args)

    #format input paths
    for key in ("config", "input_path"):
        args[key] = _format_input_path(args[key], "The path provided for '{0}' is invalid.".format(key))

    with open(args["config"], "r") as data_file:
        args["config"] = _nomalize_paths_in_config(load(data_file))

    func(**args)

def main():
    parser_description = "Helper tools for performing ArcGIS Server administrative functions."

    if not ARCPYEXT_AVAILABLE and not AGSADMIN_AVAILABLE:
        parser_description = "{0} No compatible libraries are installed, all functions are disabled. \
            Please install arcpyext or agsadmin.".format(parser_description)
    elif not ARCPYEXT_AVAILABLE:
        parser_description = "{0} 'arcpy'/'arcpyext' are not available, functions limited to RESTful service \
            interaction only!".format(parser_description)
    elif not AGSADMIN_AVAILABLE:
        parser_description = "{0} 'agsadmin' is not available, functions limited to mapping and \
            data functions.".format(parser_description)

    parser = argparse.ArgumentParser(description = parser_description, add_help = False)
    parser.add_argument("-h", "--help", action = "help", help = HELP_FLAG_TEXT)
    subparsers = parser.add_subparsers()

    # ArcPyExt-based Parsers, only added if ArcPyExt loaded (i.e. ArcPy is available/licenced)
    if ARCPYEXT_AVAILABLE:
        _create_parser_update_data(subparsers)
        _create_parser_sddraft(subparsers)
        _create_parser_sd(subparsers)
        _create_parser_publish(subparsers)
        _create_parser_save_copy(subparsers)
        _create_parser_multi_update_data(subparsers)

    if AGSADMIN_AVAILABLE:
        # Pure RESTful based parsers (always loaded, no licence required)
        agsrest_parser_parent = _create_parser_agsrest_parent()
        agsrest_servop_parent = _create_parser_agsrest_servop_parent([agsrest_parser_parent])

        _create_parser_start(subparsers, [agsrest_servop_parent])
        _create_parser_stop(subparsers, [agsrest_servop_parent])
        _create_parser_delete(subparsers, [agsrest_servop_parent])

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()