"""Script for reading sensors from board and printing result or saving to file
"""
import argparse
from datetime import datetime
import logging
from pathlib import Path
import sys
import time

import numpy as np

from oleas.helpers import (
    readout,
    get_board_from_args,
    is_valid_output_file,
    save_pickle,
    setup_logger_output,
    get_board_from_args,
    load_pedestals,
    correct_pedestals,
)
from oleas.mcp4725 import Mcp4725
from oleas.mcp4728 import Mcp4728

from naludaq.communication import ControlRegisters
from naludaq.daq import DebugDaq
from naludaq.controllers import (
    get_board_controller,
    get_readout_controller,
)
from naludaq.tools.waiter import EventWaiter

# =====================================================================
#                             CONFIGURATION
# =====================================================================
# array of gate delay values
DELAY_VALUES = np.linspace(0, 10000, 10, endpoint=True)

def dac_value(delay: int) -> float:
    """Function for computing the normalized DAC value as an arbitrary
    function of a gate delay value.

    Args:
        delay (int): gate delay

    Returns:
        float: normalized DAC value for controlling PMT gain (0-1)
    """
    # ramp function clamped 0-1, could be anything though
    ramp_start = 1000
    ramp_stop = 10_000

    ramp_slope = 1 / (ramp_stop - ramp_start)
    dac = ramp_slope * (delay - ramp_start)
    return min(max(dac, 0), 1)

# Static gate length
GATE_LENGTH = 1000

# Address/channel of the DAC
DAC_CHANNEL = 0
DAC_VREF = 0
DAC_GAIN = 1

# Time in seconds to let the PMT settle after adjusting the gain
PMT_SETTLE_TIME = 0.5

# number of events per (delay, dac) pair
NUM_CAPTURES = 3

# The window to read as (windows, lookback, write after trig)
READ_WINDOW = {
    'windows': 8,
    'lookback': 16,
    'write_after_trig': 16,
}
# ==================================================================
DAC_VALUES = np.array([dac_value(x) for x in DELAY_VALUES])


logger = logging.getLogger(__name__)


def main():
    args = parse_args(sys.argv[1:])
    if args.debug:
        setup_logger_output()
    if args.interval <= 0:
        print('Iteration interval must be a positive number')
        sys.exit(1)
    # make sure output file is valid first to avoid problems that could come up later
    if not is_valid_output_file(args.output):
        print(f'Output file is not valid: {args.output}')
        sys.exit(1)

    logger.debug('Loading pedestals from file: %s', args.pedestals)
    try:
        pedestals = load_pedestals(args.pedestals)
    except:
        print(f'Invalid pedestals file')
        sys.exit(1)

    # ==========================================
    board = get_board_from_args(args, startup=True)
    board.pedestals = pedestals

    # ==========================================
    ControlRegisters(board).write('oleas_length_a', GATE_LENGTH)
    get_readout_controller(board).set_read_window(**READ_WINDOW)

    sweep_data: list[list[list[dict]]] = []
    times: list[datetime] = []
    try:
        while True:
            iteration_start_time = time.time()
            timestamp = datetime.now()
            iteration_data: list[list[dict]] = []
            for delay, dac in zip(DELAY_VALUES, DAC_VALUES):
                # set delay/gain
                ControlRegisters(board).write('oleas_delay_a', int(delay))
                _set_dac(board, dac)

                # read events
                data: list[dict] = []
                try:
                    with readout(board, READ_WINDOW) as daq:
                        data = _read_events(board, daq, NUM_CAPTURES)
                except KeyboardInterrupt:
                    break
                except:
                    print('Error: failed to capture data!')
                iteration_data.append(data)
            sweep_data.append(iteration_data)
            times.append(timestamp)

            # wait until it's time for the next iteration
            leftover_time = args.interval - (time.time() - iteration_start_time)
            time.sleep(max(leftover_time, 0))
    except KeyboardInterrupt:
        print('Interrupted')
        pass

    # ==========================================
    print('Generating output files')
    output = {
        'dac': DAC_VALUES,
        'delay': DELAY_VALUES,
        'data': sweep_data,
        'corrected_data': correct_pedestals(sweep_data, board.params, board.pedestals),
        'times': times,
    }
    save_pickle(args.output, output)


def parse_args(argv):
    """Parse command line arguments"""
    default_model = 'aodsoc_aods'
    parser = argparse.ArgumentParser(description='Run sweep of gated PMT')
    # required
    parser.add_argument('--output', '-o', type=Path, required=True, help='Output file (pickle)')
    parser.add_argument('--serial', '-s', type=str, required=True, help='FTDI serial number of board')
    parser.add_argument('--pedestals', '-p', type=Path, required=True, help='Path to pedestals file')
    parser.add_argument('--interval', '-i', type=float, required=True, help='Time interval between iterations in seconds')

    # optional
    parser.add_argument('--model', '-m', type=str, default=default_model, help=f'Board model. Defaults to "{default_model}"')
    parser.add_argument('--baudrate', '-b', type=int, default=None, help='Baud rate. Defaults to fastest available.')
    parser.add_argument('--debug', '-d', action='store_true', help='Show debug messages')
    return parser.parse_args(argv)


def _set_dac(board, value):
    logger.info('Setting dac to %s', value)
    # Mcp4725(self._board).set_normalized_value(value)
    Mcp4728(board).set_normalized_value(
        channel=DAC_CHANNEL,
        value=value,
        vref=DAC_VREF,
        gain=DAC_GAIN,
    )
    time.sleep(PMT_SETTLE_TIME)

def _read_events(board, daq, amount):
    bc = get_board_controller(board)
    buffer = daq.output_buffer
    output = []

    for _ in range(amount):
        bc.toggle_trigger()

        for _ in range(5):
            try:
                waiter = EventWaiter(buffer, amount=1, timeout=1, interval=0.005)
                waiter.start(blocking=True)
                output.append(buffer.popleft())
            except (TimeoutError, IndexError):
                logger.info('Failed to get event, trying again...')
                bc.toggle_trigger()
                continue
            else:
                break
        else:
            logger.error('Maximum number of attempts reached. Aborting.')
    return output


if __name__ == '__main__':
    main()
