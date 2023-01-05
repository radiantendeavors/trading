"""!@package pytrader.strategies

Provides the Base Class for a Strategy.

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

@file strategies/__init__.py

    Contains global variables for the pyTrader program.

"""
# System libraries

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

@var colortext
Allows Color text on the console
"""
logger = logging.getLogger(__name__)

# ==================================================================================================
#
# Classes
#
# ==================================================================================================

# ==================================================================================================
#
# Functions
#
# ==================================================================================================
