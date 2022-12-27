#!/usr/bin/env python3
"""!@package pytrader

Algorithmic Trading Program

@author Geoff S. derber
@version HEAD
@date 2022
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

@file __init__.py

    Contains global variables for the pyTrader program.

"""
__all__ = [
    '__author__', '__contact__', '__copyright__', '__license__', '__status__',
    '__version__', 'DEBUG'
]

__author__ = 'G S Derber'
__contact__ = 'gd.github@radiantendeavors.com'
__copyright__ = 2022
__license__ = 'AGPL'
__status__ = 'Prototype'
__version__ = '0.0.2'

# ==================================================================================================
#
# Libraries
#
# ==================================================================================================
# System Libraries

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging
# Other Application Libraries

# Conditional Libraries
"""! Global Constants

@var bool DEBUG
The mode of operation; False = Normal, True = Debug.

@var int LOGLEVEL
The minimum run level
"""
DEBUG = True
LOGLEVEL = 20
"""! Logging Variables

@var logger The base logger.

@var consolehandler Sets the console handler to use color output.

@var consoleformatter Sets the format for the Console Formatter.

"""

logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)

consolehandler = logging.ColorizingStreamHandler()
consolehandler.setLevel(LOGLEVEL)
consoleformatter = logging.ConsoleLvlFormatter()
consolehandler.setFormatter(consoleformatter)

logger.addHandler(consolehandler)
