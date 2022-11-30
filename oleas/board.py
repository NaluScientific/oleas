import logging

from naludaq.board import Board, startup_board

from oleas.exceptions import BoardStartupError


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
    startup = args.startup
    logger.debug('Board arguments: model=%s, baud=%s, serial=%s, startup=%s', model, baud, serial, startup)

    try:
        board = get_board(serial, model, baud)
    except Exception as e:
        raise e

    success = True
    if startup:
        success = startup_board(board)
    if not success:
        raise BoardStartupError('Failed to start board')

    return board
