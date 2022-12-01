import logging
import time

import numpy as np

from naludaq.communication import ControlRegisters
from naludaq.daq import DebugDaq
from naludaq.controllers import (
    get_board_controller,
)
from naludaq.tools.waiter import EventWaiter

import oleas.helpers as helpers
from oleas.exceptions import DataCaptureError, SensorError
from oleas.mcp4725 import Mcp4725
from oleas.mcp4728 import Mcp4728
from oleas.nd_sweep import NdSweep
from oleas.telemetry import read_sensors


logger = logging.getLogger(__name__)
EVENT_TIMEOUT = 0.5 # seconds
EVENT_POLLING_INTERVAL = 0.001 # seconds


class GateDelayPmtDacSweep(NdSweep):

    def __init__(
            self,
            board,
            delay: np.ndarray,
            dac: np.ndarray,
            num_captures=10,
        ):
        super().__init__([delay, dac])
        self._board = board
        self._daq: DebugDaq = None
        self._attempts = 5
        self._num_captures = num_captures

        self._pmt_settle_time: float = 0
        self._read_window = None

        # configuration for the MCP4728
        self._dac_channel = 0
        self._dac_vref = 0
        self._dac_gain = 1

    def configure_dac(self, channel: int, vref: int, gain: int):
        """Set the MCP4728 DAC configuration to use.

        Args:
            channel (int): the channel number (0-4)
            vref (int): 0 (VDD) or 1 (internal 2.048 V)
            gain (int): 1 (output 0.0 to 2.048 V) or 2 (output 0.0 to 4.096 V).
        """
        self._dac_channel = channel
        self._dac_vref = vref
        self._dac_gain = gain

    def set_pmt_settling_time(self, t: float):
        """Set the amount of time to let the PMT settle for after adjusting the gain

        Args:
            t (float): time in seconds
        """
        self._pmt_settle_time = t

    def set_read_window(self, read_window: tuple):
        self._read_window = read_window

    def run(self) -> list:
        """Run the gate delay/PMT dac sweep"""
        logger.info('Running sweep')
        with helpers.readout(self._board, self._read_window) as daq:
            self._daq = daq
            return super().run()

    def _set_axis_value(self, axis: int, value: int, index: int):
        super()._set_axis_value(axis, value, index)

        if axis == 0:
            self._set_delay(value)
        elif axis == 1:
            self._set_dac(value)

    def _run_for_point(self) -> list[dict]:
        """Capture events at the current (delay, dac) coordinate

        Returns:
            list[dict]: list of events
        """
        logger.info('Capturing for next point %s', self.current_point)
        bc = get_board_controller(self._board)
        buffer = self._daq.output_buffer
        num_captures = self._num_captures
        attempts = self._attempts
        output = []

        # Read out events
        for _ in range(num_captures):
            bc.toggle_trigger()

            for _ in range(attempts):
                try:
                    waiter = EventWaiter(buffer, amount=1, timeout=EVENT_TIMEOUT, interval=EVENT_POLLING_INTERVAL)
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
                raise DataCaptureError('Maximum number of attempts reached')

        return output

    def _set_delay(self, value):
        logger.info('Setting delay to %s', value)
        self._write_control_register('oleas_delay_a', int(value))

    def _set_dac(self, value):
        logger.info('Setting dac to %s', value)
        Mcp4725(self._board).set_value(value)
        # Mcp4728(self._board).set_normalized_value(
        #     channel=self._dac_channel,
        #     value=value,
        #     vref=self._dac_vref,
        #     gain=self._dac_gain,
        # )
        time.sleep(self._pmt_settle_time)

    def _write_control_register(self, name, value):
        ControlRegisters(self._board).write(name, value)
