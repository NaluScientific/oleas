import argparse
from pathlib import Path
import logging
import time

from naludaq.board import Board, startup_board
from naludaq.daq import DebugDaq
from naludaq.controllers import (
    get_board_controller,
    get_readout_controller,
)
from naludaq.tools.waiter import EventWaiter


logger = logging.getLogger(__name__)


def get_board(serial: str, model: str='aodsoc_aods', baud=None):
    board = Board(model)
    baud = baud or max(board.params['possible_bauds'].keys())
    board.get_ftdi_connection(serial_number=serial, baud=baud)
    return board


def gate_pmt_sweep(board, low: int, high: int, count: int) -> list[dict]:

    for low




def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('output_dir', type=Path, help='Output directory')
    parser.

def main():
