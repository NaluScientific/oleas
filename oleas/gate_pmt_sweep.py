from dataclasses import dataclass
import logging

import numpy as np

from naludaq.communication import ControlRegisters

from oleas.capture import get_events
from oleas.dac7578 import DAC7578
from oleas.exceptions import DataCaptureError


logger = logging.getLogger(__name__)

@dataclass
class GatedPmtSweepConfig:
    """Convenient dataclass for bundling together all the sweep parameters
    """
    pmt_dac_values: list[int]
    gate_delay_values: list[int]
    read_window: tuple
    pmt_dac_addr: int
    pmt_dac_channel: int
    num_captures: int


def run_sweep(board, config: GatedPmtSweepConfig) -> dict:
    """Run a sweep over the gate delay and PMT gain.

    Args:
        board (Board): the board object.
        config (GatedPmtSweepConfig): the config to use for the sweep.

    Returns:
        dict: the sweep data in a dict object.
    """
    gate_delay_values = config.gate_delay_values
    pmt_dac_values = config.pmt_dac_values
    read_window = config.read_window
    num_captures = config.num_captures
    pmt_addr = config.pmt_dac_addr
    pmt_channel = config.pmt_dac_channel

    output = {
        'pmt_gains': np.repeat(pmt_dac_values, len(gate_delay_values)), # x
        'gate_delays': np.tile(gate_delay_values, len(pmt_dac_values)), # y
        'data': [None for _ in range(len(gate_delay_values)) for _ in range(len(pmt_dac_values))], # z
    }

    for i, dac_value in enumerate(pmt_dac_values):
        set_pmt_gain(board, pmt_addr, pmt_channel, dac_value)

        for j, delay in enumerate(gate_delay_values):
            set_gate_delay(board, delay)

            try:
                data = get_events(board, num_captures, read_window=read_window)
            except DataCaptureError:
                logger.error('Failed to capture data on (dac_value=%s, delay=%s)', dac_value, delay)
                raise
            output['data'][i * len(gate_delay_values) + j] = data

    return output


def set_gate_delay(board, delay: int):
    """Set the gate delay
    """
    _write_control_register(board, 'oleas_delay_a', delay) # TODO: what is this???
    _write_control_register(board, 'oleas_delay_b', delay)


def set_pmt_gain(board, addr: int, channel: int, dac_counts: int):
    """Set the PMT gain by updating the DAC

    Args:
        board (Board): board object
        addr (int): 8-bit address of DAC
        channel (int): channel on DAC to set
        dac_counts (int): new DAC value
    """
    dac = DAC7578(board, addr)
    dac.set_dacs({channel: dac_counts}) # TODO: need address and channel!


def _write_control_register(board, name: str, value: int):
    ControlRegisters(board).write(name, value)
