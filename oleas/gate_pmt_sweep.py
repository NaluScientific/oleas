
from .capture import get_events
from .exceptions import DataCaptureError


DEFAULT_NUM_CAPTURES=10
DEFAULT_READ_WINDOW=(8, 16, 16)



def move_gate(board, start, width):
    raise NotImplementedError() # TODO: need to know how to configure the gate


# TODO: need gate sweep parameters
def run_gate_sweep(board, start, stop, step, width, num_captures=DEFAULT_NUM_CAPTURES, read_window=DEFAULT_READ_WINDOW) -> dict:

    for i in range(start, stop, step):
        move_gate(board, start, width)
        events = get_events(board, num_captures, read_window=read_window)
