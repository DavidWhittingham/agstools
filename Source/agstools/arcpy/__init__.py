from ._locator import create_parser_makeloc, create_parser_rebuildloc
from ._agsconn import create_parser_agsconn
from ._dbconn import create_parser_dbconn

def load_parsers(subparsers):
    create_parser_agsconn(subparsers)
    create_parser_dbconn(subparsers)
    create_parser_makeloc(subparsers)
    create_parser_rebuildloc(subparsers)