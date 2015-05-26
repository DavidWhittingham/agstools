from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow,
                      range, round, str, super, zip)

import argparse

from agstools._helpers import create_argument_groups, namespace_to_dict

def create_db_connection(out_path, database_platform, instance, account_authentication, username = None, 
                         password = None, save_user_pass = "SAVE_USERNAME", database = None, schema = None, 
                         version_type = "TRANSACTIONAL", version = None, date = None):
    import arcpy
    from os import path

    out_path = path.abspath(out_path)

    arcpy.CreateDatabaseConnection_management(path.dirname(out_path), path.basename(out_path), database_platform,
        instance, account_authentication, username, password, save_user_pass, database, schema, version_type, version,
        date)

def create_parser_dbconn(parser):
    parser_agsconn = parser.add_parser("dbconn", add_help = False,
        help = "Creates a connection file for an ArcGIS Enterprise Database instance.")
    parser_agsconn.set_defaults(func = _process_dbconn_arguments, lib_func = create_db_connection)

    group_req, group_opt, group_flags = create_argument_groups(parser_agsconn)

    group_req.add_argument("-o", "--out-path", required = True,
        help = "The output path for the newly created connection file ('.sde').")

    group_req.add_argument("-dp", "--database-platform", required = True,
        choices = ["SQL_SERVER", "ORACLE", "DB2", "DB2ZOS", "INFORMIX", "NETEZZA", "POSTGRESQL", "TERADATA"],
        help = "The database platform for the ArcGIS Enterprise Database instance.")

    group_req.add_argument("-i", "--instance", required = True,
        help = "The database server or instance to connect to.  This varies between the different provider types. \
                See the ArcGIS Help documentation on creating database connections for more information.")

    group_opt.add_argument("-a", "--auth-mode", choices = ["DATABASE_AUTH", "OPERATING_SYSTEM_AUTH"],
        default = "DATABASE_AUTH", dest = "account_authentication",
        help = "Sets the provider for authentication credentials for the connection ('DATABASE_AUTH' is the default).")

    group_opt.add_argument("-u", "--username",
        help = "The username to the ArcGIS Server install.")

    group_opt.add_argument("-p", "--password",
        help = "The password to the ArcGIS Server install. If you wish to enter this interactively in a private way, \
                use the '-pp' flag.")

    group_opt.add_argument("-d", "--database",
        help = "The name of the database to connect to.  This is only required for the PostgreSQL and SQL Server \
                platforms.")
                
    group_opt.add_argument("--schema",
        help = "The user-schema geodatabase to connect to.  This is only applicable to Oracle databases that contain a \
                user-schema geodatabase.")

    group_opt.add_argument("--version-type", choices = ["TRANSACTIONAL", "HISTORICAL", "POINT_IN_TIME"],
        default = "TRANSACTIONAL",
        help = "Sets the type of version to connect to. \
                For HISTORICAL, if the '--version-name' parameter is not provided, the default version will be used. \
                For POINT_IN_TIME, if the '--date' parameter is not provided, the default version will be used.")

    group_opt.add_argument("--version",
        help = "The name of the transactional version to connect to.  The 'DEFAULT' version is used if no value is \
                provided.")

    group_opt.add_argument("--date",
        help = "The date of the historical version to connect to.  The 'DEFAULT' version is used if no value is \
                provided and 'HISTORICAL' is set as the version type.")

    group_flags.add_argument("--dont-save-cred", action = "store_const", dest = "save_user_pass",
        default = "SAVE_USERNAME", const = "DO_NOT_SAVE_USERNAME",
        help = "Prevents the username/password from being saved with the connection.")
        
    group_flags.add_argument("-pp", "--password-prompt", action = "store_true",
        help = "If this flag is set, you will be prompted to enter your password in a masked input field, rather \
                than supply it as visible text on the command line (for privacy).")


def _process_dbconn_arguments(args):
    args, func = namespace_to_dict(args)

    # Check if username is provided and password is not, and if so, prompt
    if args["password_prompt"] == True:
        import getpass
        if args["username"] == None:
            print("No username was supplied, please enter it now:")
            args["username"] = raw_input(" username > ")
        print("Please enter your database password:")
        # getpass doesn't support unicode at this stage, force a binary string
        args["password"] = getpass.getpass(b" password > ")
    
    args.pop("password_prompt", None)

    func(**args)