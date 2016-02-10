from __future__ import print_function, unicode_literals, absolute_import

import argparse
import imp
import sys

from ._helpers import HELP_FLAG_TEXT

ARCPYEXT_AVAILABLE = True
AGSADMIN_AVAILABLE = True

try:
    imp.find_module("arcpyext")
except ImportError:
    ARCPYEXT_AVAILABLE = False

try:
    imp.find_module("agsadmin")
except ImportError:
    AGSADMIN_AVAILABLE = False

_DIRS_TO_DELETE = []

DATA_SOURCE_TEMPLATES_HELP = """
-------------------------
CONFIGURATION INFORMATION
-------------------------
The JSON-encoded configuration file contains one mandatory key,
'dataSourceTemplates', which provides a mechanism for replacing layer data
sources using templates.

Data Source Templates
---------------------
The 'dataSourceTemplates' key contains an array of objects, with each one
taking the form of a dictionary containing two keys, "matchCriteria" and
"dataSource", both of which are also dictionaries.

Match criteria is a dictionary of key/value pairs that are compared to the
details of layers/table views.  If all listed match criteria are contained in
the layer/table view details, the template is a match and the date source
described in the "dataSource" key will be used to replace the table/layer
views data source.  Valid match keys for layers are 'name', 'longName',
'datasetName', 'dataSource', 'serviceType', 'userName', 'server', 'service',
and 'database'.  Valid match keys for table views are 'datasetName',
'dataSource', 'definitionQuery', and 'workspacePath'.  String values are
case sensitive.

Data source describes the replacement data source for a layer. As a minimum,
it should provide a "workspacePath" key that is the path (relative or absolute
to executing path) to a valid Arc workspace.  Optionally, the data source
dictionary also supports 'datasetName', 'workspaceType', and 'schema' keys,
allowing you to change these data source properties simultaneously.

Example
-------
{
    "dataSourceTemplates": [
        {
            "matchCriteria": {
                "server": "foo.server.local",
                "userName": "bar"
            },
            "dataSource": {
                "workspacePath": "./path/to/conn.sde"
            }
        }
    ]
}
"""

def main():
    parser_description = "Helper tools for performing ArcGIS Server administrative functions."

    if not ARCPYEXT_AVAILABLE and not AGSADMIN_AVAILABLE:
        parser_description = "{0} No compatible libraries are installed, only basic functions from arcpy are \
            available.  Please install arcpyext or agsadmin for additional functionality.".format(parser_description)
    elif not ARCPYEXT_AVAILABLE:
        parser_description = "{0} 'arcpy'/'arcpyext' are not available, functions limited to RESTful service \
            interaction only!".format(parser_description)
    elif not AGSADMIN_AVAILABLE:
        parser_description = "{0} 'agsadmin' is not available, functions limited to mapping and \
            data functions.".format(parser_description)

    parser = argparse.ArgumentParser(description = parser_description, add_help = False)
    parser.add_argument("-h", "--help", action = "help", help = HELP_FLAG_TEXT)
    subparsers = parser.add_subparsers()

    if ARCPYEXT_AVAILABLE:
        # arcpyext-based parsers, only added if arcpyext is available
        import agstools.arcpyext
        agstools.arcpyext.load_parsers(subparsers)

    if AGSADMIN_AVAILABLE:
        # agsadmin parsers, pure RESTful based parsers, only loaded if agsadmin is available
        import agstools.agsadmin
        agstools.agsadmin.load_parsers(subparsers)

    # pure arcpy parsers
    import agstools.arcpy
    agstools.arcpy.load_parsers(subparsers)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    try:
        args = parser.parse_args()
        args.func(args)
    finally:
        # Clean up temp directories, if any exist
        for dir in _DIRS_TO_DELETE:
            shutil.rmtree(dir)

if __name__ == "__main__":
    main()