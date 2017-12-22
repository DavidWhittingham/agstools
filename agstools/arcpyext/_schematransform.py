from __future__ import print_function, unicode_literals, absolute_import

from agstools._helpers import create_argument_groups, execute_args, format_input_path, format_output_path
from ._helpers import open_map_document

def create_parser_schema_transform(parser):
    parser_schema_transform = parser.add_parser("schematransform", add_help = False,
        help = "Bi-directional geodatabase schema transformation. Supports json and file/sde gdb formats")
    parser_schema_transform.set_defaults(func = execute_args, lib_func = transform_schema)

    group_req, group_opt, group_flags = create_argument_groups(parser_schema_transform)

    group_req.add_argument("-t", "--target", type=str, choices=["json", "gdb", "xml"],
        help = "The output target.")

    group_req.add_argument("-i", "--input", required = True,
        help = "Input file path.")

    group_req.add_argument("-o", "--output", required = True,
        help = "Output file path.")

def transform_schema(target, input, output):
    import arcpyext

    in_path = format_input_path(input)
    out_path = format_output_path(output)

    if target == "json":
        arcpyext.schematransform.to_json(in_path, out_path)
    elif target == "gdb":
        arcpyext.schematransform.to_gdb(in_path, out_path)
    elif target == "xml":
        arcpyext.schematransform.to_xml(in_path, out_path)        

    print("Done.")