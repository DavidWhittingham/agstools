from ast import literal_eval
from datetime import timedelta
from json import load
from os import path, remove, makedirs
from shutil import copy2, move
import argparse
import sys
import time

import agsadmin

try:
    import arcpyext
except:
    pass

REQUIRED_PARAMS_TEXT = "Required Arguments"
OPTIONAL_PARAMS_TEXT = "Optional Arguments"
FLAGS_TEXT = "Optional Flags"
HELP_FLAG_TEXT = "Show this help message and exit"

class StoreNameValuePairs(argparse.Action):
    """Simple argparse Action class for taking multiple string values in the form a=b and returning a dictionary. 
    Literal values (i.e. booleans, numbers) will attempt to be converted to there appropriate Python types. 
    On either side of the equals sign, double quotes can be used to contain a string that includes white space."""

    def __call__(self, parser, namespace, values, option_string=None):
        values_dict = {}
        for pair in values:
            k, v = pair.split('=')
            try:
                v = literal_eval(v)
            except SyntaxError:
                pass

            values_dict[k] = v

        setattr(namespace, self.dest, values_dict)

def delete_service(args):
    restadmin = _create_rest_admin_service(args)

    print("Deleting service...")
    restadmin.delete_service(args.name, args.type, args.folder)
    print("Service deleted.")

def map_to_sddraft(args):
    import arcpy

    _parse_args_mxd(args)

    if not args.json == None:
        args.json = _format_path(args.json, "Path to JSON settings file is invalid.")

        with open(args.json) as settings_file:
            args.settings = dict(load(settings_file).items() + args.settings.items())

    if not args.leaveExisting and not "replace_existing" in args.settings:
        args.settings["replace_existing"] = True

    print("Creating SDDraft from Map Document...")

    if args.title == None:
        args.title = path.splitext(path.basename(args.mxd))[0].strip().replace(" ", "_")

    if args.output == None:
        args.output = "{0}.sddraft".format(path.splitext(args.mxd)[0])
    else:
        args.output = _format_output(args.output)

    map = arcpy.mapping.MapDocument(args.mxd)
    sd_draft = arcpyext.mapping.convert_map_to_service_draft(map, args.output, args.title, folder_name = args.folder)

    if not args.settings == None:
        def set_arg(sd_draft, k, v):
            if hasattr(sd_draft, k):
                setattr(sd_draft, k, v)

        # min instances must be set before max instances, so we get it out of the way
        if "min_instances" in args.settings:
            set_arg(sd_draft, "min_instances", args.settings["min_instances"])
            del args.settings["min_instances"]
      
        for k, v in args.settings.items():
            set_arg(sd_draft, k, v)

    sd_draft.save()

    print("Done, SD Draft created at: {0}".format(args.output))

def publish_sd(args):
    import arcpy

    args.sd = _format_path(args.sd, "Path to the service definition is invalid.")
    args.conn = _format_path(args.conn, "Path to ArcGIS Server Connection file is invalid.")

    print("Publishing service definition...")

    arcpy.UploadServiceDefinition_server(args.sd, args.conn)

    print("Done, service definition published.")

def save_a_copy(args):
    import arcpy

    _parse_args_mxd(args)
    args.output = _format_output(args.output)

    print("Opening map document: {0}".format(args.mxd))
    map = arcpy.mapping.MapDocument(args.mxd)

    print("Saving a copy to: {0}".format(args.output))
    if args.version == None:
        map.saveACopy(args.output)
    else:
        map.saveACopy(args.output, args.version)

    print("Done.")
    

def sddraft_to_sd(args):
    args.sddraft = _format_path(args.sddraft, "Path to service definition draft is invalid.")

    print("Creating service definition from draft...")

    if args.output == None:
        args.output = "{0}.sd".format(path.splitext(args.sddraft)[0])
    else:
        args.output = _format_output(args.output)

    if args.persist == True:
        sddraft_backup = "{0}.sddraft.bak".format(path.splitext(args.sddraft)[0])
        copy2(args.sddraft, sddraft_backup)

    sd_draft = arcpyext.mapping.SDDraft(args.sddraft)

    arcpyext.mapping.convert_service_draft_to_staged_service(sd_draft, args.output)

    if args.persist == True:
        move(sddraft_backup, args.sddraft)

    print("Done, service definition created at: {0}".format(args.output))

def update_data(args):
    import arcpy

    _parse_args_mxd(args)
    args.data = _format_path(args.data, "Path to the JSON-encoded data sources file is invalid.")
    
    with open(args.data, "r") as data_file:
        datasources_list = load(data_file)

    print("Opening Map Document...")
    map = arcpy.mapping.MapDocument(args.mxd)

    print("Updating data sources...")
    arcpyext.mapping.change_data_sources(map, datasources_list)

    print("Saving map document...")
    if args.output != None:
        args.output = _format_output(args.output)
        if path.exists(args.output):
            remove(args.output)

        map.saveACopy(args.output)
    else:
        map.save()

    print("Done.")

def start_service(args):
    restadmin = _create_rest_admin_service(args)

    serv = restadmin.get_service(args.name, args.type, args.folder)

    print("Starting service...")
    serv.start_service()
    print("Service started.")

def stop_service(args):
    restadmin = _create_rest_admin_service(args)

    serv = restadmin.get_service(args.name, args.type, args.folder)

    print("Stopping service...")
    serv.stop_service()
    print("Service stopped.")

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

def _create_parser_agsrest_parent():
    parser_agsrest_parent = argparse.ArgumentParser(add_help = False)

    group_req, group_opt, group_flags = _create_argument_groups(parser_agsrest_parent, include_help_flag = False)

    group_req = parser_agsrest_parent.add_argument_group("Required Arguments")
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
    group_opt.add_argument("--timedelta", type=int,
        help = "The number of minutes (plus/minus) your server is from UTC. This is used when calculating key expiry \
            time when performing non-SSL encrypted communications. Defaults to your local offset.")

    group_flags.add_argument("--ssl", action = "store_true",
        help = "Forces the use of TLS/SSL when processing the request.")

    return parser_agsrest_parent

def _create_parser_agsrest_servop_parent(parents):
    agsrest_servop_parent = argparse.ArgumentParser(add_help = False, parents = parents)
    agsrest_servop_parent.set_defaults(func = start_service)

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
    parser_copy.set_defaults(func = save_a_copy)

    group_req, group_opt, group_flags = _create_argument_groups(parser_copy)

    group_req.add_argument("-m", "--mxd",
        help = "File path to the map document (*.mxd) to copy.")

    group_req.add_argument("-o", "--output",
        help = "The path on which to save the copy of the map document.")

    group_opt.add_argument("-v", "--version", type=str, choices=["9.0", "9.1", "9.2", "9.3", "10.0", "10.1"],
        help = "The output version number for the saved copy.")


def _create_parser_delete(parser, parents):
    """Creates a sub-parser for deleting an ArcGIS Server Service."""

    parser_delete = parser.add_parser("delete", parents = parents, add_help = False,
        help = "Deletes a service on an ArcGIS Server instance.")
    parser_delete.set_defaults(func = delete_service)
    
def _create_parser_publish(parser):
    parser_publish = parser.add_parser("publish", add_help = False,
        help = "Publishes a service definition to an ArcGIS Server instance.")
    parser_publish.set_defaults(func = publish_sd)

    group_req, group_opt, group_flags = _create_argument_groups(parser_publish, opt_group = False)

    group_req.add_argument("-s", "--sd", required = True,
        help = "File path to the service definition (*.sd) to publish.")
    group_req.add_argument("-c", "--conn", required = True,
        help = "File path to the ArcGIS Server Connection File (*.ags) for the server to publish the file to.")

def _create_parser_sd(parser):
    parser_sd = parser.add_parser("sd", add_help = False,
        help = "Stages an ArcGIS Server service definition draft into a service definition ready for publishing (this \
            will by default delete the draft).")
    parser_sd.set_defaults(func = sddraft_to_sd)

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
        help = "Converts a map document (*.mxd) to an ArcGIS Server service definition draft.")
    parser_sddraft.set_defaults(func = map_to_sddraft)

    group_req, group_opt, group_flags = _create_argument_groups(parser_sddraft)

    group_req.add_argument("-m", "--mxd", required = True,
        help = "Path to the map document to be converted.")

    group_opt.add_argument("-t", "--title", required = False,
        help = "Title of the published service.  Defaults to the map document file name (spaces in the file name will \
            be replaced by underscores).")
    group_opt.add_argument("-o", "--output", required = False,
        help = "The path to save the SD Draft to. If left out, defaults to saving with the same filename/path as the \
            MXD (use '*.sddraft' as extension).")
    group_opt.add_argument("-f", "--folder", required = False,
        help = "The server folder to publish the service to.  If left out, defaults to the root directory.")
    group_opt.add_argument("-j", "--json", required = False,
        help = "File path to a JSON-formatted file that contains key/value pairs of the additional properties you wish \
            to set on the service definition draft.")
    group_opt.add_argument("-s", "--settings", default = {}, required = False, nargs = "*", action = StoreNameValuePairs,
        help = "Additional key/value settings (in the form 'key=value') that will be processed by the SD Draft creator.")
    
    group_flags.add_argument("-l", "--leaveExisting", default = False, action = "store_true",
        help = "Prevents an existing service from being overwritten.")

def _create_parser_start(parser, parents):
    parser_start = parser.add_parser("start", parents = parents, add_help = False,
        help = "Starts a service on an ArcGIS Server instance.")
    parser_start.set_defaults(func = start_service)

def _create_parser_stop(parser, parents):
    parser_stop = parser.add_parser("stop", parents = parents, add_help = False,
        help = "Stops a service on an ArcGIS Server instance.")
    parser_stop.set_defaults(func = stop_service)

def _create_parser_update_data(parser):
    """Creates a sub-parser for updating the data sources of a map document."""

    parser_update_data = parser.add_parser("updatedata", add_help = False,
        help = "Updates the workspace (data source) of each layer in a map document.")
    parser_update_data.set_defaults(func = update_data)

    group_req, group_opt, group_flags = _create_argument_groups(parser_update_data)

    group_req.add_argument("-m", "--mxd", required = True,
        help = "The map document to be updated.")
    group_req.add_argument("-d", "--data", required = True,
        help = "The path to a JSON-encoded document containing a list of workspaces, one per layer. \
            Group layers or layers that shouldn't be updated should have a value of 'null'.")

    group_opt.add_argument("-o", "--output", 
        help = "The path to a location you would like the map document saved to, \
            in the event that you do not wish to overwrite the original.")

def _create_rest_admin_service(args):
    if args.port == None:
        args.port = 6080

    if args.timedelta == None:
        args.timedelta = time.timezone / -60 if time.daylight == 0 else time.altzone / -60

    if not args.proxy == None:
        args.proxy = {"http": args.proxy, "https": args.proxy}

    return agsadmin.RestAdmin(args.server, args.username, args.password, 
        utc_delta = timedelta(minutes = args.timedelta), proxies = args.proxy, port = args.port)

def _format_path(filepath, message = None):
    if not path.exists(filepath):
        raise IOError(message)
    else:
        return path.abspath(filepath)

def _format_output(filepath):
    filepath = path.abspath(filepath)

    dir = path.dirname(filepath)
    if not path.exists(dir):
        makedirs(dir)

    return filepath

def _parse_args_mxd(args):
    args.mxd = _format_path(args.mxd, "Path to map document is invalid.")

def main():
    if "arcpyext" in sys.modules:
        arcpy_available = True
        parser_description = "Helper tools for performing ArcGIS Server administrative functions."
    else:
        arcpy_available = False
        parser_description = "Helper tools for performing ArcGIS Server administrative functions. \
            ArcPy is not available, functions limited to RESTful service interaction only!"

    parser = argparse.ArgumentParser(description = parser_description)
    subparsers = parser.add_subparsers()

    # ArcPyExt-based Parsers, only added if ArcPyExt loaded (i.e. ArcPy is available/licenced)
    if arcpy_available:
        _create_parser_update_data(subparsers)
        _create_parser_sddraft(subparsers)
        _create_parser_sd(subparsers)
        _create_parser_publish(subparsers)
        _create_parser_save_copy(subparsers)

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