from agstools._helpers import create_argument_groups, execute_args, format_output_path
from ._mxd_helpers import open_map_document

def create_parser_save_copy(parser):
    parser_copy = parser.add_parser("copy", add_help = False,
        help = "Saves a copy of an ArcGIS map document, optionally in a different output version.")
    parser_copy.set_defaults(func = execute_args, lib_func = save_a_copy)

    group_req, group_opt, group_flags = create_argument_groups(parser_copy)

    group_req.add_argument("-m", "--mxd", required = True,
        help = "File path to the map document (*.mxd) to copy.")

    group_req.add_argument("-o", "--output", required = True,
        help = "The path on which to save the copy of the map document.")

    group_opt.add_argument("-v", "--version", type=str, choices=["8.3", "9.0", "9.2", "9.3", "10.0", "10.1", "10.3"],
        help = "The output version number for the saved copy.")

def save_a_copy(mxd, output_path, version = None):
    import arcpy

    output_path = format_output_path(output_path)

    print("Opening map document: {0}".format(mxd))
    map = open_map_document(mxd)

    print("Saving a copy to: {0}".format(output_path))
    if version == None:
        map.saveACopy(output_path)
    else:
        map.saveACopy(output_path, version)

    print("Done.")