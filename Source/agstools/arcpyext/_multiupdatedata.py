from __future__ import print_function, unicode_literals, absolute_import

import argparse
import fnmatch

from json import load
from os import path, listdir

from agstools._agstools import DATA_SOURCE_TEMPLATES_HELP
from agstools._helpers import create_argument_groups, format_input_path, format_output_path, namespace_to_dict, normalize_paths_in_config
from ._updatedata import update_data

MXD_FILETYPE_PATH_FILTER = "*.mxd"

def create_parser_multi_update_data(parser):
    """Creates a sub-parser for updating the data sources of a map document."""

    help_info = "Updates the workspace (data source) of each layer in a map document, for every map document within a given folder."

    parser_update_data = parser.add_parser("multiupdatedata", add_help = False,
        help = help_info, description = help_info,
        formatter_class = argparse.RawDescriptionHelpFormatter)
    parser_update_data.set_defaults(func = _process_arguments, lib_func = update_data_folder)

    group_req, group_opt, group_flags = create_argument_groups(parser_update_data)

    group_req.add_argument("-i", "--input-path", required = True,
        help = "The absolute or relative path to the directory containing all MXDs to be updated.")

    group_req.add_argument("-o", "--output-path", required = True,
        help = "The absolute or relative path to the directory to output MXDs to.")

    group_req.add_argument("-c", "--config", required = True,
        help = "The absolute or relative path to the JSON-encoded configuration data (see below).")

    group_flags.add_argument("-r", "--reload-symbology", action = "store_true",
        help = "Forces the output MXD to have its symbology set based on the input MXD (ArcMap will drop symbology if the underlying data source is even slightly different).")

    parser_update_data.epilog = DATA_SOURCE_TEMPLATES_HELP

def update_data_folder(input_path, output_path, data_source_templates, reload_symbology = False):
    import arcpy
    import arcpyext

    mxd_list = _filter_uptodate_mxds(input_path, output_path)

    for mxd_in in mxd_list:
        mxd_out = format_output_path(path.join(output_path, mxd_in))
        mxd_in = path.join(input_path, mxd_in)

        update_data(mxd_in, data_source_templates, mxd_out, reload_symbology)

def _compare_last_modified(base_file, other_file):
    return path.getmtime(other_file) - path.getmtime(base_file)

def _filter_uptodate_mxds(input_path, output_path):
    """Compares the modified timestamps of MXDs in one folder to MXDs in another and returns a list of MXDs from the
    input path that are more recent then those on the output path."""
    mxd_list = _get_file_list(input_path, MXD_FILETYPE_PATH_FILTER)

    return [filename for filename in mxd_list if (
        not path.exists(path.join(output_path, filename)) or
        (_compare_last_modified(path.join(input_path, filename), path.join(output_path, filename)) < 0))
    ]

def _get_file_list(dir_path, path_filter):
    dir_path = format_input_path(dir_path, "MXD Directory does not exist or could not be found.")
    path_list = []

    def _list_files_in_dir(dir):
        for f in fnmatch.filter(filter(path.isfile, [path.join(dir, f) for f in listdir(dir)]), path_filter):
            path_list.append(path.relpath(f, dir_path))

    _list_files_in_dir(dir_path)
    sub_dir_list = filter(path.isdir, [path.join(dir_path, sd) for sd in listdir(dir_path)])

    for sub_dir in sub_dir_list:
        _list_files_in_dir(sub_dir)

    return path_list

def _process_arguments(args):
    args, func = namespace_to_dict(args)

    #format input paths
    for key in ("config", "input_path"):
        args[key] = format_input_path(args[key], "The path provided for '{0}' is invalid.".format(key))

    with open(args["config"], "r") as data_file:
        config = normalize_paths_in_config(load(data_file), args["config"])
        args["data_source_templates"] = config["dataSourceTemplates"]
        args.pop("config")

    func(**args)