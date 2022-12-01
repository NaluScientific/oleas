from naludaq.devices.i2c_device import I2CDevice


DEFAULT_ADDRESS = 0b1100010
SINGLE_WRITE_COMMAND = 0b01011000


class Mcp4728:
    """Controller for the MCP4728"""

    def __init__(self, board, address: int = DEFAULT_ADDRESS):
        self._device = I2CDevice(board, address)

    def set_normalized_value(self, channel: int, value: float, vref: int=0, gain: int=1):
        """Set normalized value (0.0 - 1.0)

        Args:
            channel (int): channel number (0-4)
            value (int): 12-bit value (0 - 4095)
            vref (int): 0 (VDD) or 1 (internal 2.048 V)
            gain (int): 1 (output 0.0 to 2.048 V) or 2 (output 0.0 to 4.096 V).
        """
        if not 0.0 <= value <= 1.0:
            raise ValueError('Value must be 0.0 to 1.0')
        self.set_value(channel, int(value * 4095.0), vref, gain)

    def set_value(self, channel: int, value: int, vref=0, gain=1):
        """Set 12-bit value (0 - 4095)

        Args:
            channel (int): channel number (0-4)
            value (int): 12-bit value (0 - 4095)
            vref (int): 0 (VDD) or 1 (internal 2.048 V)
            gain (int): 1 (output 0.0 to 2.048 V) or 2 (output 0.0 to 4.096 V).
        """
        if not 0 <= value <= 4095:
            raise ValueError('Value must be 0 to 4095')
        if channel not in range(4):
            raise ValueError('Channel must be 0-4')
        if vref not in [0, 1]:
            raise ValueError('VREF must be 0 or 1')
        if gain not in [1, 2]:
            raise ValueError('Gain must be 1 or 2')

        buf = bytearray(3)
        buf[0] = SINGLE_WRITE_COMMAND | (channel << 1)
        buf[1] = (vref << 7) | (gain << 4) | ((value >> 8) & 0xF)
        buf[2] = value & 0xFF

        self._device.send_write_command(buf, check_ack=False)
