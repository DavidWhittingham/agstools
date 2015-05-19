from __future__ import print_function, unicode_literals, absolute_import

from agstools._helpers import format_input_path

def config_to_settings(args):
    """Merge configuration file settings with any command-line provided settings."""
    if "config" in args:
        if args["config"] != None:
            if "settings" in args and args["settings"] != None:
                args["settings"].update(args["config"]["serviceSettings"])
            else:
                args["settings"] = args["config"]["serviceSettings"]
        args.pop("config", None)
    return args

def open_map_document(mxd):
    import arcpy
    if isinstance(mxd, basestring):
        return arcpy.mapping.MapDocument(format_input_path(mxd))
    return mxd