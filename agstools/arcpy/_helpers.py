def get_temp_ags_conn():
    import getpass
    import arcpy
    
    print("No connection file provided.  Please input the following:")
    server = raw_input(" protocol://server/instance/admin:port > ")
    username = raw_input(" username > ")
    password = getpass.getpass(" password > ")
    
    temp_folder = _create_temp_folder()

    arcpy.mapping.CreateGISServerConnectionFile("PUBLISH_GIS_SERVICES", temp_folder, 'publish.ags',
        "http://{0}/arcgis/admin".format(server), "ARCGIS_SERVER", False, temp_folder, username, password, True)