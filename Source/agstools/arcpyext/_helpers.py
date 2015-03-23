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

def set_settings_on_sddraft(sd_draft, settings):
    def set_arg(sd_draft, k, v):
        if hasattr(sd_draft, k):
            setattr(sd_draft, k, v)

    # min instances must be set before max instances, so we get it out of the way
    if "min_instances" in settings:
        set_arg(sd_draft, "min_instances", settings["min_instances"])
        del settings["min_instances"]

    for k, v in settings.items():
        set_arg(sd_draft, k, v)