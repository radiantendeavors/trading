#!/usr/bin/env python3
"""!@package pytrader

Contains global variables for the pyTrader program.

@author G S Derber
@version HEAD
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

@file pytrader/__init__.py

Contains global variables for the pyTrader program.

"""
__all__ = [
    '__author__', '__contact__', '__copyright__', '__license__', '__status__',
    '__version__', 'DEBUG'
]

__author__ = 'G S Derber'
__contact__ = 'gd.github@radiantendeavors.com'
__copyright__ = 2023
__license__ = 'AGPL'
__status__ = 'Prototype'
__version__ = '0.2.2'

# ==================================================================================================
#
# Libraries
#
# ==================================================================================================
# Standard Libraries

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging
# Other Application Libraries

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The mode of operation; False = Normal, True = Debug.
DEBUG = True
## The default log level
LOGLEVEL = 20
"""! Logging Variables

@var logger The base logger.

@var consolehandler 

@var consoleformatter 

"""

## An instance of the logging class
logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)

## The console handler - Used to set the console handler to use color output.
consolehandler = logging.ColorizingStreamHandler()
consolehandler.setLevel(LOGLEVEL)

## The console formatter - Sets the format for the Console Formatter.
consoleformatter = logging.ConsoleLvlFormatter()
consolehandler.setFormatter(consoleformatter)

logger.addHandler(consolehandler)
