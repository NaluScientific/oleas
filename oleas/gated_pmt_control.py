from naludaq.communication import ControlRegisters

from oleas.dac7578 import DAC7578




def _write_control_register(board, name: str, value: int):
    ControlRegisters(board).write(name, value)
