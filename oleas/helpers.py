from contextlib import contextmanager
import logging
import pickle
import gzip

from naludaq.board import Board, startup_board
from naludaq.communication import ControlRegisters
from naludaq.daq import DebugDaq
from naludaq.controllers import (
    get_board_controller,
    get_readout_controller,
    get_gainstage_controller,
)
from naludaq.tools.pedestals.pedestals_correcter import PedestalsCorrecter


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


def get_board_from_args(args, startup: bool=False) -> Board:
    """Get board from command line arguments

    Args:
        startup (bool): whether to start up the board

    Returns:
        Board: the board with a connection, and optionally started up.
    """
    model = args.model
    baud = args.baudrate
    serial = args.serial
    logger.debug('Board arguments: model=%s, baud=%s, serial=%s', model, baud, serial)

    try:
        board = get_board(serial, model, baud)
    except Exception as e:
        raise e

    if startup:
        startup_board(board)

    return board


@contextmanager
def readout(board, read_window: dict) -> DebugDaq:
    """Start a readout/capture for the board.

    This function is a context manager. When used in a `with` block,
    it yields a daq object and cleans up properly when the context exits.

    Example:
    ```
    with readout(board) as daq:
        get_board_controller(board).toggle_trigger()
        time.sleep(1)
    ```

    Args:
        board (Board): board object
        read_window (tuple): read window as (windows, lookback, write after trigger)
    """
    rc = get_readout_controller(board)
    rc.set_read_window(**read_window)

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


def load_pedestals(path) -> dict:
    """Load pedestals from disk.

    Args:
        path (Path | str): path to pedestals file

    Returns:
        dict: pedestals dict
    """
    with gzip.GzipFile(path, 'rb') as f:
        return pickle.load(f)


def correct_pedestals(data: list[list[list[dict]]], params: dict, pedestals: dict) -> list[list[list[dict]]]:
    """Apply pedestals correction to the sweep data.

    Args:
        data (list[list[list[dict]]]): parsed sweep data
        params (dict): board params
        pedestals (dict): pedestals to use

    Returns:
        list[list[list[dict]]]: the pedestals corrected sweep data. Returns [] if there was an error.
    """
    correct = PedestalsCorrecter(params, pedestals).run
    try:
        corrected_data = [
            [
                [
                    correct(event, correct_in_place=False)
                    for event in dac
                ] for dac in delay
            ] for delay in data
        ]
    except Exception as e:
        logger.error('Failed to correct pedestals: %s', e)
        corrected_data = []
    return corrected_data


def correct_pedestals_for_capture(data: list[list[dict]], params: dict, pedestals: dict) -> list[list[dict]]:
    """Apply pedestals correction to the capture data.

    Args:
        data (list[list[dict]]): parsed capture data
        params (dict): board params
        pedestals (dict): pedestals to use

    Returns:
        list[list[dict]]: the pedestals corrected capture data. Returns [] if there was an error.
    """
    correct = PedestalsCorrecter(params, pedestals).run
    try:
        corrected_data = [
            [
                correct(event, correct_in_place=False)
                for event in step
            ] for step in data
        ]
    except Exception as e:
        logger.error('Failed to correct pedestals: %s', e)
        corrected_data = []
    return corrected_data


def select_external_i2c_bus(board):
    """Set I2C communication to use the external bus."""
    ControlRegisters(board).write('i2c_bus_sel', 1)


def set_default_gain_stages(board):
    """Set the gain stages on the board to the defaults:
    - CH0: external input
    - CH1: 8x CH0
    - CH2: 8x CH1
    - CH3: 8x CH2
    """
    gc = get_gainstage_controller(board)
    gc.ch0_external_input()
    gc.ch1_8x_ch0()
    gc.ch2_8x_ch1()
    gc.ch3_8x_ch2() # use of channel 3 isn't planned, but might come in handy
