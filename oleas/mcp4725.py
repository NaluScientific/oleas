from naludaq.devices.i2c_device import I2CDevice

DEFAULT_ADDRESS = 0b01100010


class MCP4725:

    def __init__(self, board, address: int = DEFAULT_ADDRESS) -> None:
        self._device = I2CDevice(board, address)

    def set_value(self, val: int) -> None:
        """Set 16-bit value (0-65535). Lower four bits are discarded."""
        if not 0 <= val <= 65535:
            raise ValueError('Value must be 0 to 65535')
        self.set_raw_value(val >> 4)

    def set_normalized_value(self, val: float) -> None:
        """Set normalized value (0.0 - 1.0)"""
        if not 0.0 <= val <= 1.0:
            raise ValueError('Value must be 0.0 to 1.0')
        self.set_raw_value(int(val * 4095.0))

    def set_raw_value(self, val: int) -> None:
        """Set 12-bit value (0 - 4095)"""
        if not 0 <= val <= 4095:
            raise ValueError('Value must be 0 to 4095')

        buff = bytearray(2)
        buff[0] = (val >> 8) & 0xF
        buff[1] = val & 0xFF
        self._device.send_write_command(buff, check_ack=False)
