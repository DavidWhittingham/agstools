from ._delete import create_parser_delete
from ._rest_helpers import create_parser_agsrest_parent, create_parser_agsrest_servop_parent
from ._start import create_parser_start
from ._stop import create_parser_stop

def load_parsers(subparsers):
    agsrest_parser_parent = create_parser_agsrest_parent()
    agsrest_servop_parent = create_parser_agsrest_servop_parent([agsrest_parser_parent])

    create_parser_start(subparsers, [agsrest_servop_parent])
    create_parser_stop(subparsers, [agsrest_servop_parent])
    create_parser_delete(subparsers, [agsrest_servop_parent])