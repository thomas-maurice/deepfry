#!/usr/bin/env python3

import logging
import sys

LEVEL = logging.WARNING
LOGGER = None

def set_level(lvl=logging.WARNING):
    global LEVEL
    LEVEL = lvl

def get_logger(lvl=logging.WARNING):
    global LOGGER
    if LOGGER is None:
        logger = logging.getLogger(__name__)
        logger.setLevel(LEVEL)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(LEVEL)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        LOGGER = logger
        return LOGGER
    else:
        return LOGGER