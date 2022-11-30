from contextlib import contextmanager
import logging
import pickle

from naludaq.board import Board
from naludaq.daq import DebugDaq
from naludaq.controllers import (
    get_board_controller,
    get_readout_controller,
)


logger = logging.getLogger(__name__)



def save_pickle(path, obj):
    """Save object to pickle file"""
    try:
        with open(path, 'wb') as f:
            pickle.dump(obj, f)
    except:
        raise


def is_valid_output_file(file) -> bool:
    """Check if file is good for writing"""
    valid = True
    try:
        open(file, 'w')
    except:
        valid = False
    return valid


def setup_logger_output():
    """Direct logger output to console"""
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(name)-30s [%(levelname)-6s]: %(message)s'))
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger


def get_board(serial: str, model: str='aodsoc_aods', baud=None):
    """Connect to a board

    Args:
        serial (str): the board serial number
        model (str): board model
        baud (int): baud rate, or None to use fastest available.

    Returns:
        _type_: _description_
    """
    board = Board(model)
    baud = baud or max(board.params['possible_bauds'].keys())
    board.get_ftdi_connection(serial_number=serial, baud=baud)
    return board


def get_board_from_args(args) -> Board:
    """Get board from command line arguments"""
    model = args.model
    baud = args.baudrate
    serial = args.serial
    logger.debug('Board arguments: model=%s, baud=%s, serial=%s', model, baud, serial)

    try:
        board = get_board(serial, model, baud)
    except Exception as e:
        raise e

    return board


@contextmanager
def readout(board, read_window: tuple=None) -> DebugDaq:
    """Start a readout/capture for the board.

    This function is a context manager. When used in a `with` block,
    it yields a daq object and cleans up properly when the context exits.

    Example:
    ```
    with readout(board) as daq:
        get_board_controller(board).toggle_trigger()
        time.sleep(1)
    ```
    """
    if read_window:
        rc = get_readout_controller(board)
        rc.set_read_window(*read_window)

    logger.info('Starting readout')

    daq = DebugDaq(board)
    bc = get_board_controller(board)
    daq.start_capture()
    bc.start_readout('ext')
    try:
        yield daq
    except:
        raise
    finally:
        logger.info('Stopping readout')
        bc = get_board_controller(board)
        bc.stop_readout()
        daq.stop_capture()
