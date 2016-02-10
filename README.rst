agstools
========

Command-line tool for managing ArcGIS (in particular ArcGIS Server), including performing data maintenance, and service publishing automation.

Depends on *arcpyext* (https://github.com/DavidWhittingham/arcpyext) and *agsadmin* (https://github.com/DavidWhittingham/agsadmin) for functionality.  *agsadmin* doesn't require any ArcGIS software or licence, but *arcpyext* does.  Tested/maintained on Python 2.7.

Once installed, simply run ``agstools`` from a shell prompt (assuming the Python scripts directory is in your ``PATH`` environment variable).

Help is available on the command line tool with the ``-h``/``--help`` switch.  The main help screen is reproduced below::

    usage: agstools-script.py [-h]
                              {sddraft,imagesddraft,gpsddraft,sd,updatedata,multiupdatedata,publish,copy,start,stop,delete}
                              ...

    Helper tools for performing ArcGIS Server administrative functions.

    positional arguments:
      {sddraft,imagesddraft,gpsddraft,sd,updatedata,multiupdatedata,publish,copy,start,stop,delete}
        sddraft             Converts a map document (*.mxd) to an ArcGIS Server
                            service definition draft.
        imagesddraft        Creates a service definition draft for an Image
                            Service from a raster layer.
        gpsddraft           Creates a service definition draft for a Geo-
                            processing Service from a (Python) Toolbox.
        sd                  Stages an ArcGIS Server service definition draft into
                            a service definition ready for publishing (this will
                            by default delete the draft).
        updatedata          Updates the workspace (data source) of each layer in a
                            map document.
        multiupdatedata     Updates the workspace (data source) of each layer in a
                            map document, for every map document within a given
                            folder.
        publish             Publishes a service definition to an ArcGIS Server
                            instance.
        copy                Saves a copy of an ArcGIS map document, optionally in
                            a different output version.
        start               Starts a service on an ArcGIS Server instance.
        stop                Stops a service on an ArcGIS Server instance.
        delete              Deletes a service on an ArcGIS Server instance.

    optional arguments:
      -h, --help            Show this help message and exit.
