from __future__ import print_function, unicode_literals, absolute_import

from os import path
from shutil import copy2, move

from agstools._helpers import create_argument_groups, execute_args, format_input_path, format_output_path

def create_parser_sd(parser):
    parser_sd = parser.add_parser("sd", add_help = False,
        help = "Stages an ArcGIS Server service definition draft into a service definition ready for publishing (this \
            will by default delete the draft).")
    parser_sd.set_defaults(func = execute_args, lib_func = sddraft_to_sd)

    group_req, group_opt, group_flags = create_argument_groups(parser_sd)

    group_req.add_argument("-s", "--sddraft", required = True,
        help = "File path to the service definition draft (*.sddraft) to finalize.")

    group_opt.add_argument("-o", "--output",
        help = "The path on which to save the staged service definition. If left out, defaults to saving with the \
            same filename/path as the draft (use '*.sd' as extension).")

    group_flags.add_argument("-p", "--persist", default = False, action = "store_true",
        help = "After staging the Service Defintion, re-save the draft in it's original location")

def sddraft_to_sd(sddraft, output = None, persist = False):
    import arcpyext

    print("Creating service definition from draft...")

    sddraft = format_input_path(sddraft, "Path to service definition draft is invalid.")

    if output == None:
        output = "{0}.sd".format(path.splitext(sddraft)[0])
    else:
        output = format_output_path(output)

    if persist == True:
        sd_draft_backup_path = "{0}.sddraft.bak".format(path.splitext(sddraft)[0])
        copy2(sddraft, sd_draft_backup_path)

    arcpyext.publishing.convert_service_draft_to_staged_service(sddraft, output)

    if persist == True:
        move(sd_draft_backup_path, sddraft)

    print("Done, service definition created at: {0}".format(output))