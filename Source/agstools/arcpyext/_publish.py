from agstools._helpers import create_argument_groups, execute_args

def create_parser_publish(parser):
    parser_publish = parser.add_parser("publish", add_help = False,
        help = "Publishes a service definition to an ArcGIS Server instance.")
    parser_publish.set_defaults(func = execute_args, lib_func = publish_sd)

    group_req, group_opt, group_flags = create_argument_groups(parser_publish, opt_group = False)

    group_req.add_argument("-s", "--sd", required = True,
        help = "File path to the service definition (*.sd) to publish.")
    group_req.add_argument("-c", "--conn", required = True,
        help = "File path to the ArcGIS Server Connection File (*.ags) for the server to publish the file to.")

def publish_sd(sd, conn):
    import arcpy

    sd = _format_input_path(sd, "Path to the service definition is invalid.")
    conn = _format_input_path(conn, "Path to ArcGIS Server Connection file is invalid.")

    print("Publishing service definition...")

    arcpy.UploadServiceDefinition_server(sd, conn)

    print("Done, service definition published.")