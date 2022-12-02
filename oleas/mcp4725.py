from naludaq.devices.i2c_device import I2CDevice

DEFAULT_ADDRESS = 0b1100010


class Mcp4725:

    def __init__(self, board, address: int = DEFAULT_ADDRESS):
        self._device = I2CDevice(board, address)

    def set_normalized_value(self, value: float):
        """Set normalized value (0.0 - 1.0)"""
        if not 0.0 <= value <= 1.0:
            raise ValueError('Value must be 0.0 to 1.0')
        self.set_value(round(value * 4095.0))

    def set_value(self, value: int):
        """Set 12-bit value (0 - 4095)"""
        if not 0 <= value <= 4095:
            raise ValueError('Value must be 0 to 4095')

        buff = bytearray(2)
        buff[0] = (value >> 8) & 0xF
        buff[1] = value & 0xFF
        self._device.send_write_command(buff, check_ack=False)
