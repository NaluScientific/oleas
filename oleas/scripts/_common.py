import argparse
from pathlib import Path


DEFAULT_BOARD_MODEL = 'aodsoc_aods'
DEFAULT_STARTUP_FLAG = True



def add_board_arguments(parser: argparse.ArgumentParser):
    # required
    parser.add_argument('--serial', '-s', type=bool, required=True, help='FTDI serial number of board')

    # optional
    parser.add_argument('--model', '-m', type=str, default=DEFAULT_BOARD_MODEL, help=f'Board model. Defaults to "{DEFAULT_BOARD_MODEL}"')
    parser.add_argument('--baudrate', '-b', type=int, default=None, help='Baud rate. Defaults to fastest available.')



def add_debug_argument(parser: argparse.ArgumentParser):
    parser.add_argument('--debug', '-d', action='store_true', help='Show debug messages')
