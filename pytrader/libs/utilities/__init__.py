"""!@package pytrader.libs.utilities

General Utility functions for pytrader

@author G. S. Derber
@date 2022-2023
@copyright GNU Affero General Public License

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.


@file pytrader/libs/utilities/__init__.py
"""
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
