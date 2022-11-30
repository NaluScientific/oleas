"""Script for reading sensors from board and printing result or saving to file
"""
import argparse
import logging
from pathlib import Path
import sys

import numpy as np

from oleas.helpers import get_board_from_args
from oleas.gate_pmt_sweep import GateDelayPmtDacSweep
from oleas.helpers import (
    is_valid_output_file,
    save_pickle,
    setup_logger_output,
    get_board_from_args,
)


logger = logging.getLogger(__name__)

# ======================================
# array of gate delay values
DELAY_VALUES = np.arange(0, 1000, 100)

# array of pmt dac values
DAC_VALUES = np.arange(0, 1000, 200)

# number of events per (delay, dac) pair
NUM_CAPTURES = 3

# Address/channel of the DAC
DAC_ADDRESS = 0x00
DAC_CHANNEL = 0

# Time in seconds to let the PMT settle after adjusting the gain
PMT_SETTLE_TIME = 0.5

# The window to read as (windows, lookback, write after trig)
READ_WINDOW = (8, 16, 16)
# ======================================


def main():
    args = parse_args(sys.argv[1:])
    if args.debug:
        setup_logger_output()

    # make sure output file is valid first to avoid wasting time later
    if not is_valid_output_file(args.output):
        print(f'Output file is not valid: {args.output}')
        sys.exit(1)


    # ==========================================
    board = get_board_from_args(args)

    sweeper = GateDelayPmtDacSweep(board, DELAY_VALUES, DAC_VALUES, NUM_CAPTURES)
    sweeper.set_read_window(READ_WINDOW)
    sweeper.configure_dac(DAC_ADDRESS, DAC_CHANNEL)
    sweeper.set_pmt_settling_time(PMT_SETTLE_TIME)
    sweep_data = sweeper.run()
    output = {
        'dac': DAC_VALUES,
        'delay': DELAY_VALUES,
        'data': sweep_data,
    }

    # ==========================================

    save_pickle(args.output, output)


def parse_args(argv):
    """Parse command line arguments"""
    default_model = 'aodsoc_aods'
    parser = argparse.ArgumentParser(description='Run sweep of gated PMT')
    # required
    parser.add_argument('--output', '-o', type=Path, required=True, help='Output file (pickle)')
    parser.add_argument('--serial', '-s', type=str, required=True, help='FTDI serial number of board')

    # optional
    parser.add_argument('--model', '-m', type=str, default=default_model, help=f'Board model. Defaults to "{default_model}"')
    parser.add_argument('--baudrate', '-b', type=int, default=None, help='Baud rate. Defaults to fastest available.')
    parser.add_argument('--debug', '-d', action='store_true', help='Show debug messages')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main()
