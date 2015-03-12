from ._copy import create_parser_save_copy
from ._imagesddraft import create_parser_image_sddraft
from ._multiupdatedata import create_parser_multi_update_data
from ._publish import create_parser_publish
from ._sddraft import create_parser_sddraft
from ._sd import create_parser_sd
from ._updatedata import create_parser_updatedata

def load_parsers(subparsers):
    create_parser_sddraft(subparsers)
    create_parser_image_sddraft(subparsers)
    create_parser_sd(subparsers)
    create_parser_updatedata(subparsers)
    create_parser_multi_update_data(subparsers)
    create_parser_publish(subparsers)
    create_parser_save_copy(subparsers)