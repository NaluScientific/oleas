"""Script for reading sensors from board and printing result or saving to file
"""
import argparse
import logging
from pathlib import Path
import sys

from oleas.board import get_board_from_args
from oleas.scripts._common import add_board_arguments, add_debug_argument
from oleas.gate_pmt_sweep import run_sweep
from oleas.helpers import is_valid_output_file, save_pickle, setup_logger_output


logger = logging.getLogger(__name__)


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Run sweep of gated PMT')
    parser.add_argument('--output', '-o', type=Path, required=True, help='Output file (pickle)')
    add_board_arguments(parser)
    add_debug_argument(parser)
    return parser.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])
    output_file = args.output
    debug = args.debug

    if debug:
        setup_logger_output()

    # make sure output file is valid first to avoid wasting time later
    if not is_valid_output_file(output_file):
        print(f'Output file is not valid: {output_file}')
        sys.exit(1)

    board = get_board_from_args(args)
    sweep_result = run_sweep(board)
    save_pickle(output_file, sweep_result)



if __name__ == '__main__':
    main()
