import logging

from naludaq.board import Board


logger = logging.getLogger(__name__)


def get_board(serial: str, model: str='aodsoc_aods', baud=None):
    board = Board(model)
    baud = baud or max(board.params['possible_bauds'].keys())
    board.get_ftdi_connection(serial_number=serial, baud=baud)
    return board


def get_board_from_args(args) -> Board:
    model = args.model
    baud = args.baud
    serial = args.serial
    logger.debug('Board arguments: model=%s, baud=%s, serial=%s', model, baud, serial)

    try:
        board = get_board(serial, model, baud)
    except Exception as e:
        raise e

    return board
