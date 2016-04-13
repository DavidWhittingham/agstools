from __future__ import print_function, unicode_literals, absolute_import

from agstools.agsadmin._rest_helpers import create_parser_agsrest_parent
from agstools.agsadmin._rest_helpers import create_parser_agsrest_machine_parent
from agstools.agsadmin._rest_helpers import create_parser_agsrest_servop_parent
from agstools.agsadmin._machine_start import create_parser_machine_start
from agstools.agsadmin._machine_stop import create_parser_machine_stop
from agstools.agsadmin._service_delete import create_parser_service_delete
from agstools.agsadmin._service_start import create_parser_service_start
from agstools.agsadmin._service_stop import create_parser_service_stop

def load_parsers(subparsers):
    agsrest_parser_parent = create_parser_agsrest_parent()
    agsrest_servop_parent = create_parser_agsrest_servop_parent([agsrest_parser_parent])
    agsrest_machine_parent = create_parser_agsrest_machine_parent([agsrest_parser_parent])

    create_parser_machine_start(subparsers, [agsrest_machine_parent])
    create_parser_machine_stop(subparsers, [agsrest_machine_parent])
    create_parser_service_start(subparsers, [agsrest_servop_parent])
    create_parser_service_stop(subparsers, [agsrest_servop_parent])
    create_parser_service_delete(subparsers, [agsrest_servop_parent])