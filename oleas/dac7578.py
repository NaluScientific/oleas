import logging
import time

from naludaq.communication import sendI2cCommand


LOGGER = logging.getLogger(__name__)


class DAC7578:
    """DAC7578 controller class
    """

    def __init__(self, board, addr: int) -> None:
        """Controller for the DAC7578 DAC.

        Args:
            addr (int): 8-bit address
            board (Board): the board object.
            send_delay (float): the time to wait between sequential I2C
                writes in seconds.
        """
        self._board = board
        self._addr = addr
        self._send_delay = 0.001
        self._write_cmd = 0b0011

    def set_dacs(self, values: dict[int, int]):
        """Writes the values to the DAC for each chip channel given.

        The values written come from the board object.

        Args:
            values (dict[int, int]): dict of {channel: counts}

        Raises:
            ValueError if any of the internal DAC values on the board
                are out of bounds.
            ConnectionError if the I2C commands could not be sent
        """
        board = self._board
        addr = self._addr
        send_delay = self._send_delay

        for channel, value in values.items():
            words = [
                f'0011{channel:04b}',
                f'{(value >> 4 & 0xFF):08b}',
                f'{(value << 4 & 0xFF):08b}',
            ]
            LOGGER.debug(f"Sending DAC Command - ADDR: {addr}\t WORDS:{words}")
            if not sendI2cCommand(board, addr, words):
                raise ConnectionError('Failed to write I2C DAC')
            time.sleep(send_delay)
