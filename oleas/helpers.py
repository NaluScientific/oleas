import logging
import pickle
import yaml

import numpy as np


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


def setup_logger_output():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(name)-30s [%(levelname)-6s]: %(message)s'))
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger
