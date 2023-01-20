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
    correct_pedestals_for_capture,
    readout,
    get_board_from_args,
    is_valid_output_file,
    save_pickle,
    select_external_i2c_bus,
    set_default_gain_stages,
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
    get_gainstage_controller,
)
from naludaq.tools.waiter import EventWaiter

# =====================================================================
#                             CONFIGURATION
# =====================================================================
# array of gate delay values
NUM_POINTS = 5
DELAY_VALUES = np.linspace(start=0, stop=20, num=NUM_POINTS, endpoint=True)

# Address/channel of the DAC
DAC_CHANNEL_VALUES = [
    np.linspace(start=0, stop=1, num=NUM_POINTS, endpoint=True), # DAC CHANNEL 0 (Board Channel 0)
    np.linspace(start=0, stop=0.4, num=NUM_POINTS, endpoint=True), # DAC CHANNEL 1 (Board Channel 4)
]
DAC_VREF = 0
DAC_GAIN = 1

# Loop Length (each increment is x2 to length)
LOOP_LENGTH = 9

# Static gate length
GATE_LENGTH_A = 40
GATE_LENGTH_B = 40

# Polarity
POLARITY_A = 1
POLARITY_B = 0

# Delay
DELAY_A = 0 # This delay is being varied from DELAY_VALUES
DELAY_B = 0

# Time in seconds to let the PMT settle after adjusting the gain
PMT_SETTLE_TIME = 0.5

# number of events per (delay, dac) pair
NUM_CAPTURES = 3

# The window to read as (windows, lookback, write after trig)
READ_WINDOW = {
    'windows': 40,
    'lookback': 40,
    'write_after_trig': 20,
}
# ==================================================================

logger = logging.getLogger(__name__)


def main():
    args = parse_args(sys.argv[1:])
    if args.debug:
        setup_logger_output()
    if args.interval <= 0:
        print('Iteration interval must be a positive number')
        sys.exit(1)
    # make sure output file is valid first to avoid problems that could come up later
    output_dir: Path = Path(args.output).resolve()
    if not output_dir.exists():
        print(f'Output directory does not exist: {output_dir}')
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

    # ==========================================
    bc = get_board_controller(board)
    bc.set_oleas_enabled(en_trig = 1, en_a = 1, en_b = 1)
    bc.set_oleas_loop(LOOP_LENGTH)
    bc.set_oleas_a(GATE_LENGTH_A, DELAY_A, POLARITY_A)
    bc.set_oleas_b(GATE_LENGTH_B, DELAY_B, POLARITY_B)
    
    get_readout_controller(board).set_read_window(**READ_WINDOW)

    try:
        while True:
            iteration_start_time = time.time()
            timestamp = datetime.now()
            iteration_data: list[list[dict]] = []
            for idx, delay in enumerate(DELAY_VALUES):
                # set delay/gain
                ControlRegisters(board).write('oleas_delay_a', int(delay))
                _set_dac(board, idx)

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

            output_file = output_dir / timestamp.strftime("%Y-%m-%dT %H-%M-%S.pkl")
            output = {
                'dac': DAC_CHANNEL_VALUES,
                'delay': DELAY_VALUES,
                'data': iteration_data,
                'corrected_data': correct_pedestals_for_capture(iteration_data, board.params, board.pedestals),
                'time': timestamp,
            }
            try:
                print(f'Saving output to: {output_file}')
                save_pickle(output_file, output)
            except:
                print('Failed to save output file!')

            # wait until it's time for the next iteration
            leftover_time = args.interval - (time.time() - iteration_start_time)
            time.sleep(max(leftover_time, 0))
    except KeyboardInterrupt:
        print('Interrupted')
        pass
    finally:
        bc.set_oleas_enabled(en_trig = 0, en_a = 0, en_b = 0)

def parse_args(argv):
    """Parse command line arguments"""
    default_model = 'aodsoc_aods'
    parser = argparse.ArgumentParser(description='Run sweep of gated PMT')
    # required
    parser.add_argument('--output', '-o', type=Path, required=True, help='Output directory')
    parser.add_argument('--serial', '-s', type=str, required=True, help='FTDI serial number of board')
    parser.add_argument('--pedestals', '-p', type=Path, required=True, help='Path to pedestals file')
    parser.add_argument('--interval', '-i', type=float, required=True, help='Time interval between iterations in seconds')

    # optional
    parser.add_argument('--model', '-m', type=str, default=default_model, help=f'Board model. Defaults to "{default_model}"')
    parser.add_argument('--baudrate', '-b', type=int, default=None, help='Baud rate. Defaults to fastest available.')
    parser.add_argument('--debug', '-d', action='store_true', help='Show debug messages')
    return parser.parse_args(argv)


def _set_dac(board, idx):
    logger.info('Setting dac to %s', np.array(DAC_CHANNEL_VALUES)[:, idx])
    # Mcp4725(self._board).set_normalized_value(value)
    for dac_channel, dac_value in enumerate(np.array(DAC_CHANNEL_VALUES)[:, idx]):
        print(f"Setting dac_channel {dac_channel} to {dac_value}")
        Mcp4728(board).set_normalized_value(
        channel=dac_channel,
        value=dac_value,
        vref=DAC_VREF,
        gain=DAC_GAIN,
    )
    # Mcp4728(board).set_normalized_value(
    #     channel=DAC_CHANNEL,
    #     value=value,
    #     vref=DAC_VREF,
    #     gain=DAC_GAIN,
    # )
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
