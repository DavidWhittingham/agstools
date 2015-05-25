from ._locator import create_parser_makeloc, create_parser_rebuildloc

def load_parsers(subparsers):
    create_parser_makeloc(subparsers)
    create_parser_rebuildloc(subparsers)