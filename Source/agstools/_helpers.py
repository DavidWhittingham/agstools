from __future__ import print_function, unicode_literals, absolute_import

from datetime import timedelta
from json import load
from os import path, makedirs

FLAGS_TEXT = "optional flags"
HELP_FLAG_TEXT = "Show this help message and exit."
OPTIONAL_PARAMS_TEXT = "optional arguments"
REQUIRED_PARAMS_TEXT = "required arguments"

def create_argument_groups(parser, req_group = True, opt_group = True, flags_group = True, include_help_flag = True):
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

def execute_args(args):
    args, func = namespace_to_dict(args)
    func(**args)

def format_input_path(filepath, message = None, work_dir = None):
    if work_dir != None and path.isabs(filepath) == False:
       filepath = path.normpath(path.join(path.abspath(work_dir), filepath))
    if not path.exists(filepath):
        raise IOError(message)
    else:
        return path.abspath(filepath)

def format_output_path(filepath):
    filepath = path.abspath(filepath)

    dir = path.dirname(filepath)
    if not path.exists(dir):
        makedirs(dir)

    return filepath

def namespace_to_dict(args):
    # This has lots of stuff specific to the various subparsers.
    # Now that they are broken out, this should be refactored.

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

def nomalize_paths_in_config(config, filepath):
    if config.has_key("dataSourceTemplates"):
        for template in config["dataSourceTemplates"]:
            if template["dataSource"].has_key("workspacePath"):
                try:
                    config_work_dir = path.dirname(filepath)
                    template["dataSource"]["workspacePath"] = format_input_path(
                        template["dataSource"]["workspacePath"],
                        work_dir = config_work_dir)
                except IOError:
                    print("Could not find full path for workspace path '{0}' in config.".format(
                        template["dataSource"]["workspacePath"]))
    return config

def _create_rest_admin_service(server, username, password, instance, port, utc_delta, proxy, ssl):
    import agsadmin

    if not proxy == None:
        proxy = {"http": proxy, "https": proxy}

    return agsadmin.RestAdmin(server, username, password, instance_name = instance, utc_delta = timedelta(minutes = utc_delta),
        proxies = proxy, port = port, use_ssl = ssl)

def _read_json_file(file_path):
    file_path = format_input_path(file_path, "Path to the JSON-encoded data sources file is invalid.")

    with open(file_path, "r") as data_file:
        return load(data_file)