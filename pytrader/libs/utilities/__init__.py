#!/usr/bin/env python3
# ==================================================================================================
#
# pytrader
#
# ==================================================================================================
# System Libraries
import importlib

# System Library Overrides
from pytrader.libs.system import logging
# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def get_plugin_function(*args, **kwargs):
    program = kwargs['program']
    command = kwargs['cmd']
    import_path = kwargs['import_path']

    logger.debug("Program: %s", program)
    logger.debug("Program: %s", command)
    logger.debug("Program: %s", import_path)

    module_name = import_path + program

    try:
        logger.debug("Attempting to import module: %s", module_name)
        module = importlib.import_module(module_name, __name__)
        return getattr(module, command)
    except ImportError as msg:
        logger.error(msg)
        raise ImportError(msg)
    except AttributeError as msg:
        logger.error(msg)
        raise AttributeError(msg)
