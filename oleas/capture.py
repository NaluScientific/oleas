from collections import deque
import logging

from naludaq.daq import DebugDaq
from naludaq.controllers import (
    get_board_controller,
    get_readout_controller,
)
from naludaq.tools.waiter import EventWaiter

from .exceptions import DataCaptureError


logger = logging.getLogger(__name__)


def get_events(board, count: int, read_window: tuple, attempts: int=5) -> list[dict]:
    """Get one or more events.

    Args:
        board (Board): the board object
        count (int): number of events to read
        read_window (tuple): read window tuple: (windows, lookback, write after trig)
        attempts (int): Number of attempts to read each event. Defaults to 5.

    Returns:
        list[dict]: list of events
    """
    daq = DebugDaq(board)
    daq.start_capture()
    start_readout(board, read_window=read_window)
    try:
        events = _capture_data(board, daq.output_buffer, count, attempts)
    except DataCaptureError:
        raise
    finally:
        stop_readout(board)
        daq.stop_capture()

    return events


def _capture_data(board, daq_buffer: deque, count: int, attempts: int):
    output = []
    daq_buffer.clear()
    for i in range(count):
        logger.info(f'Fetching event {i}...')
        for i in range(attempts):
            send_trigger(board)
            try:
                waiter = EventWaiter(daq_buffer, timeout=1)
                waiter.start(blocking=True)
                output.append(daq_buffer.popleft())
            except (TimeoutError, IndexError):
                logger.info('Failed to get event, trying again...')
                continue
            else:
                break
        else:
            logger.error('Maximum number of attempts reached. Aborting.')
            raise DataCaptureError('Maximum number of attempts reached')
    return output


def start_readout(board, read_window: tuple):
    """Start the readout"""
    rc = get_readout_controller(board)
    bc = get_board_controller(board)

    rc.set_read_window(*read_window)
    bc.start_readout('ext')


def stop_readout(board):
    """Stop an ongoing readout"""
    bc = get_board_controller(board)
    bc.stop_readout()


def send_trigger(board):
    """Send trigger to the board"""
    get_board_controller(board).toggle_trigger()
