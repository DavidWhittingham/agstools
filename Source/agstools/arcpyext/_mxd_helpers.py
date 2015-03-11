from agstools._helpers import format_input_path

def open_map_document(mxd):
    import arcpy
    if isinstance(mxd, basestring):
        return arcpy.mapping.MapDocument(format_input_path(mxd))
    return mxd