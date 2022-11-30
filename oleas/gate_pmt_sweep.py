from dataclasses import dataclass
import logging

import numpy as np

from naludaq.communication import ControlRegisters

from oleas.capture import get_events
from oleas.config import settings
from oleas.dac7578 import DAC7578
from oleas.exceptions import DataCaptureError, SensorError
from oleas.telemetry import read_sensors


logger = logging.getLogger(__name__)



def run_sweep(board) -> dict:
    """Run a sweep over the gate delay and PMT gain.
    Uses dynaconf settings.

    Args:
        board (Board): the board object.

    Returns:
        dict: the sweep data in a dict object.
    """
    gate_delays = np.linspace(
        settings.sweep.gate_delay_start,
        settings.sweep.gate_delay_stop,
        settings.sweep.steps
    ).astype(int)
    pmt_gains = np.linspace(
        settings.sweep.pmt_dac_start,
        settings.sweep.pmt_dac_stop,
        settings.sweep.steps
    ).astype(int)
    num_captures = settings.readout_settings.num_captures
    read_window = (
        settings.readout_settings.windows,
        settings.readout_settings.lookback,
        settings.readout_settings.write_after_trig,
    )

    output = {
        'pmt_gains': pmt_gains,
        'gate_delays': gate_delays,
        'data': [],
        'sensors': [],
    }

    for dac_value, delay in zip(pmt_gains, gate_delays):
        set_pmt_gain(board, dac_value)
        set_gate_delay(board, delay)

        # Read X events
        try:
            data = get_events(board, num_captures, read_window=read_window)
            output['data'].append(data)
        except DataCaptureError:
            logger.error('Failed to capture data for (dac_value=%s, delay=%s)', dac_value, delay)
            raise

        # Read all sensors
        sensors = {}
        try:
            sensors = read_sensors(board)
        except SensorError:
            logger.error('Failed to read sensors for (dac_value=%s, delay=%s)', dac_value, delay)
            pass
        output['sensors'].append(sensors)

    return output


def set_gate_delay(board, delay: int):
    """Set the gate delay
    """
    _write_control_register(board, 'oleas_delay_a', delay) # TODO: what is this???
    _write_control_register(board, 'oleas_delay_b', delay)


def set_pmt_gain(board, dac_counts: int):
    """Set the PMT gain by updating the DAC

    Args:
        board (Board): board object
        dac_counts (int): new DAC value
    """
    address = settings.pmt_dac.address
    channel = settings.pmt_dac.channel
    dac = DAC7578(board, address)
    dac.set_dacs({channel: dac_counts})


def _write_control_register(board, name: str, value: int):
    ControlRegisters(board).write(name, value)
