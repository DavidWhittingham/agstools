from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow,
                      range, round, str, super, zip)

import argparse

from agstools._helpers import create_argument_groups, namespace_to_dict

def create_ags_connection(connection_type, out_path, server_url, username = None, password = None, server_type = "ARCGIS_SERVER",
        use_arcgis_desktop_staging_folder = True, staging_folder_path = None, save_username_password = True):
    import arcpy
    from os import path
    
    out_path = path.abspath(out_path)
    staging_folder_path = path.abspath(staging_folder_path)
    
    # Connection types other than "use" require a username/password.  Check it
    if connection_type != "USE_GIS_SERVICES" and (username == None or username.isspace()
                                                  or password == None or password.isspace()):
        raise ValueError("Username/password cannot be None when creating a publish or admin connection.")
    
    arcpy.mapping.CreateGISServerConnectionFile(connection_type, path.dirname(out_path), path.basename(out_path),
        server_url, server_type, use_arcgis_desktop_staging_folder, staging_folder_path, username, password,
        save_username_password)

def create_parser_agsconn(parser):
    parser_agsconn = parser.add_parser("agsconn", add_help = False,
        help = "Creates a connection file for an ArcGIS Server install.",
        formatter_class = argparse.RawDescriptionHelpFormatter)
    parser_agsconn.set_defaults(func = _process_agsconn_arguments, lib_func = create_ags_connection)

    group_req, group_opt, group_flags = create_argument_groups(parser_agsconn)

    group_req.add_argument("-t", "--connection-type", required = True, choices = ["use", "publish", "admin"],
        help = "The type of ArcGIS Server connection that is to be created.")

    group_req.add_argument("-o", "--out-path", required = True,
        help = "The output path for the newly created connection file.")

    group_req.add_argument("-s", "--server-url", required = True,
        help = "The URL of the ArcGIS Server install. For 'use' type connections, the URL should be in the form \
            'http://server:port/instance/services', otherwise it should be in the form \
            'http://server:port/instance/admin'.")

    group_opt.add_argument("-u", "--username",
        help = "The username to the ArcGIS Server install.")

    group_opt.add_argument("-p", "--password",
        help = "The password to the ArcGIS Server install. If username is provided, but password is omitted, agstools \
            will prompt you whilst hiding input (for privacy).")

    group_opt.add_argument("--server-type", choices = ["arcgis", "spatial"], default = "arcgis",
        help = "The type of server this connection will connect to, either ArcGIS Server or Spatial Data Server.")

    group_opt.add_argument("--staging-folder", dest = "staging_folder_path",
        help = "For publishing and administrative connections, an alternative staging location can be used if desired. \
            Otherwise, the default ArcGIS for Desktop location is used.")

    group_flags.add_argument("--dont-save-cred", action = "store_false", dest = "save_username_password",
        help = "Prevents the password from being saved with the connection.")

def _process_agsconn_arguments(args):
    args, func = namespace_to_dict(args)

    # change connection_type and server_type to full values
    replace_dict = {
        "use": "USE_GIS_SERVICES",
        "publish": "PUBLISH_GIS_SERVICES",
        "admin": "ADMINISTER_GIS_SERVICES",
        "arcgis": "ARCGIS_SERVER",
        "spatial": "SPATIAL_DATA_SERVER"
    }
    args["connection_type"] = replace_dict[args["connection_type"]]
    args["server_type"] = replace_dict[args["server_type"]]
    
    # Check if username is provided and password is not, and if so, prompt
    if args["username"] != None and args["password"] == None:
        import getpass
        print("Username provided without password, please enter password now.")
        # getpass doesn't support unicode at this stage, force a binary string
        args["password"] = getpass.getpass(b" password > ")
    
    func(**args)