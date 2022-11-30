"""Script for reading sensors from board and printing result or saving to file
"""
import argparse
import logging
from pathlib import Path
import sys

from oleas.board import get_board_from_args
from oleas.scripts._common import add_board_arguments, add_output_argument
from oleas.gate_pmt_sweep import run_sweep
from oleas.helpers import fancy_print, is_valid_output_file, load_yaml_into_sweep_config, save_pickle, setup_logger_output


logger = logging.getLogger(__name__)


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Read sensors to stdout or file')
    add_board_arguments(parser)
    add_output_argument(parser, required=True)
    parser.add_argument('--config', type=Path, required=True, help='Sweep configuration file (YAML)')
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    output_file = args.output
    config_file = args.config
    debug = args.debug

    if debug:
        setup_logger_output()
    # make sure output file is valid first to avoid wasting time later
    if not is_valid_output_file(output_file):
        print(f'Output file is not valid: {output_file}')
        sys.exit(1)

    sweep_config = load_yaml_into_sweep_config(config_file)

    board = get_board_from_args(args)
    sweep_result = run_sweep(board, sweep_config)
    save_pickle(output_file, sweep_result)




if __name__ == '__main__':
    main(sys.argv[1:])
