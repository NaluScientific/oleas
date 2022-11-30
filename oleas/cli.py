import argparse

DEFAULT_BOARD_MODEL = 'aodsoc_aods'
DEFAULT_STARTUP_FLAG = True



def add_board_arguments(parser: argparse.ArgumentParser):
    parser.add_argument('--model', '-m', type=str, default=DEFAULT_BOARD_MODEL, help=f'Board model. Defaults to "{DEFAULT_BOARD_MODEL}"')
    parser.add_argument('--baudrate', '-b', type=int, default=None, help='Baud rate. Defaults to fastest available.')
    parser.add_argument('--serial', '-s', type=bool, required=True, help='FTDI serial number of board')
    parser.add_argument('--startup', type=bool, default=DEFAULT_STARTUP_FLAG, help=f'Whether to start up the board. Defaults to "{DEFAULT_STARTUP_FLAG}"')
