"""Script for reading sensors from board and printing result or saving to file
"""
import argparse
from pathlib import Path
import sys

from oleas.board import get_board_from_args
from oleas.cli import add_board_arguments
from oleas.helpers import save_pickle
from oleas.telemetry import read_sensors


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Read sensors to stdout or file')
    add_board_arguments(parser)
    parser.add_argument('--output', '-o', type=Path, default=None, help='Output file (pickle)')
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)

    board = get_board_from_args(args)
    telem = read_sensors(board)

    if args.output is None:
        print(telem)
    else:
        print(f'Saving output to {args.output}')
        save_pickle(telem, args.output)



if __name__ == '__main__':
    main(sys.argv[1:])
