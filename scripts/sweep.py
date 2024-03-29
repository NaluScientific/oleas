"""Script for reading sensors from board and printing result or saving to file
"""
import argparse
import logging
from pathlib import Path
import sys

import numpy as np

from naludaq.communication import ControlRegisters
from naludaq.controllers import get_gainstage_controller

from oleas.gate_pmt_sweep import GateDelayPmtDacSweep
from oleas.helpers import (
    get_board_from_args,
    is_valid_output_file,
    save_pickle,
    setup_logger_output,
    get_board_from_args,
    load_pedestals,
    correct_pedestals,
    select_external_i2c_bus,
    set_default_gain_stages,
)

# =====================================================================
#                             CONFIGURATION
# =====================================================================
# array of gate delay values
DELAY_VALUES = np.arange(0, 1000, 100)

# array of normalized dac values
DAC_VALUES = np.linspace(0.0, 1.0, 10)

# number of events per (delay, dac) pair
NUM_CAPTURES = 3

# Address/channel of the DAC
DAC_CHANNEL = 0
DAC_VREF = 0
DAC_GAIN = 1

# Time in seconds to let the PMT settle after adjusting the gain
PMT_SETTLE_TIME = 0.5

# The window to read as (windows, lookback, write after trig)
READ_WINDOW = {
    'windows': 8,
    'lookback': 16,
    'write_after_trig': 16,
}
# ==================================================================


logger = logging.getLogger(__name__)


def main():
    args = parse_args(sys.argv[1:])
    if args.debug:
        setup_logger_output()

    # make sure output file is valid first to avoid problems that could come up later
    if not is_valid_output_file(args.output):
        print(f'Output file is not valid: {args.output}')
        sys.exit(1)

    if args.config:
        config_path: Path = Path(args.config).resolve()
        if not config_path.exists():
            print(f'Config file does not exist: {config_path}')
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
    select_external_i2c_bus(board)
    set_default_gain_stages(board)

    # Set up the sweep controller
    sweeper = GateDelayPmtDacSweep(board, DELAY_VALUES, DAC_VALUES, NUM_CAPTURES)
    sweeper.set_read_window(READ_WINDOW)
    sweeper.configure_dac(DAC_CHANNEL, DAC_VREF, DAC_GAIN)
    sweeper.set_pmt_settling_time(PMT_SETTLE_TIME)

    # Run the sweep
    sweep_data = sweeper.run()

    # ==========================================
    output = {
        'dac': DAC_VALUES,
        'delay': DELAY_VALUES,
        'data': sweep_data,
        'corrected_data': correct_pedestals(sweep_data, board.params, board.pedestals),
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

    # optional
    parser.add_argument('--model', '-m', type=str, default=default_model, help=f'Board model. Defaults to "{default_model}"')
    parser.add_argument('--baudrate', '-b', type=int, default=None, help='Baud rate. Defaults to fastest available.')
    parser.add_argument('--config', '-c', type=Path, default=None, help='Configuration file to startup the board')
    parser.add_argument('--debug', '-d', action='store_true', help='Show debug messages')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main()
