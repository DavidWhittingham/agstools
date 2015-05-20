from __future__ import print_function, unicode_literals, absolute_import

import argparse
import tempfile
import random
import string

from json import load
from os import path, remove
from shutil import rmtree

from agstools._helpers import create_argument_groups, namespace_to_dict, normalize_paths_in_config
from agstools._agstools import DATA_SOURCE_TEMPLATES_HELP
from ._helpers import open_map_document

def create_parser_updatedata(parser):
    """Creates a sub-parser for updating the data sources of a map document."""

    parser_update_data = parser.add_parser("updatedata", add_help = False,
        help = "Updates the workspace (data source) of each layer in a map document.",
        formatter_class = argparse.RawDescriptionHelpFormatter)
    parser_update_data.set_defaults(func = _process_arguments, lib_func = update_data)

    group_req, group_opt, group_flags = create_argument_groups(parser_update_data)

    group_req.add_argument("-m", "--mxd", required = True,
        help = "The map document to be updated.")
    group_req.add_argument("-c", "--config", required = True,
        help = "The absolute or relative path to the JSON-encoded configuration data (see below).")

    group_opt.add_argument("-o", "--output-path",
        help = "The path to a location you would like the map document saved to, \
            in the event that you do not wish to overwrite the original.")

    group_flags.add_argument("-r", "--reload-symbology", action = "store_true",
        help = "Forces the output MXD to have its symbology set based on the input MXD (ArcMap will drop symbology if the underlying data source is even slightly different).")

    parser_update_data.epilog = DATA_SOURCE_TEMPLATES_HELP

def update_data(mxd, config, output_path = None, reload_symbology = False):
    import arcpyext

    if output_path != None:
        # have to do this at the top because opening a map document changes the working directory of the environment
        output_path = _format_output_path(output_path)

    mxd = open_map_document(mxd)
    working_folder = path.join(tempfile.gettempdir(), "agstools")

    # we introduce a random element to the working folder path so that collisions don't occur when running in parallel
    random_exec_num = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
    working_folder = path.join(working_folder, random_exec_num)

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
        if path.exists(output_path):
            remove(output_path)

        mxd.saveACopy(output_path)
    else:
        mxd.save()

    if path.exists(working_folder):
        rmtree(working_folder)

    print("Done.")

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

def _save_layers(mxd, output_path):
    import arcpy

    layers = [[layer for layer in arcpy.mapping.ListLayers(df)] for df in arcpy.mapping.ListDataFrames(mxd)]

    for (df_no, df) in enumerate(layers):
        df_path = path.join(output_path, str(df_no))

        for (layer_no, layer) in enumerate(df):
            layer_output_path = format_output_path(path.join(df_path, str(layer_no) + ".lyr"))
            layer.saveACopy (layer_output_path)

def _process_arguments(args):
    args, func = namespace_to_dict(args)

    with open(args["config"], "r") as data_file:
        args["config"] = normalize_paths_in_config(load(data_file), args["config"])

    func(**args)