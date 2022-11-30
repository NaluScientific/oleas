import logging
import pickle
import yaml

import numpy as np

from oleas.exceptions import SweepConfigError
from oleas.gate_pmt_sweep import GatedPmtSweepConfig


def save_pickle(obj, path):
    try:
        with open(path, 'wb') as f:
            pickle.dump(obj, f)
    except:
        raise


def is_valid_output_file(file) -> bool:
    valid = True
    try:
        open(file, 'w')
    except:
        valid = False
    return valid


def load_yaml_into_sweep_config(file) -> GatedPmtSweepConfig:
    """Load config yaml into sweep config object"""
    config_dict = None
    try:
        with open(file) as f:
            config_dict = yaml.safe_load(f)
    except (FileNotFoundError, OSError, Exception) as e:
        raise SweepConfigError('Failed to load config file') from e
    try:
        return _dict_to_config(config_dict)
    except (TypeError, KeyError, Exception) as e:
        raise SweepConfigError('Config file is malformed')


def _dict_to_config(config_dict: dict) -> GatedPmtSweepConfig:
    """Parse config dict into a sweep config object."""
    sweep_values = lambda d: np.linspace(d['start'], d['stop'], d['steps']).astype(int)

    return GatedPmtSweepConfig(
        pmt_dac_values=sweep_values(config_dict['pmt_dac_values']),
        gate_delay_values=sweep_values(config_dict['gate_dac_values']),
        read_window=(
            config_dict['read_window']['windows'],
            config_dict['read_window']['lookback'],
            config_dict['read_window']['write_after_trig']
        ),
        pmt_dac_addr=config_dict['pmt_dac']['address'],
        pmt_dac_addr=config_dict['pmt_dac']['channel'],
    )




def fancy_print(line: str, width=60):
    print('-' * width)
    print(line.center(width, ' '))
    print('-' * width)




def setup_logger_output():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(name)-30s [%(levelname)-6s]: %(message)s'))
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger
