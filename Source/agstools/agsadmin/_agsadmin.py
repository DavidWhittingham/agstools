from __future__ import print_function, unicode_literals, absolute_import

from agstools.agsadmin._delete import create_parser_delete
from agstools.agsadmin._rest_helpers import create_parser_agsrest_parent, create_parser_agsrest_servop_parent
from agstools.agsadmin._start import create_parser_start
from agstools.agsadmin._stop import create_parser_stop

def load_parsers(subparsers):
    agsrest_parser_parent = create_parser_agsrest_parent()
    agsrest_servop_parent = create_parser_agsrest_servop_parent([agsrest_parser_parent])

    create_parser_start(subparsers, [agsrest_servop_parent])
    create_parser_stop(subparsers, [agsrest_servop_parent])
    create_parser_delete(subparsers, [agsrest_servop_parent])