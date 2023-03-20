"""!@package pytrader.libs.applications.strategy

The main user interface for the trading program.

@author Geoff S. Derber
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

@file pytrader/libs/applications/trader/__init__.py
"""
# Standard Libraries
import random

import sys
import time

# 3rd Party Libraries

# Application Libraries
# Standard Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs import utilities

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

"""
logger = logging.getLogger(__name__)

## The python formatted location of the strategies
IMPORT_PATH = "pytrader.strategies."


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class StrategyProcess():

    def run(self, strategy_list):
        for i in strategy_list:
            strategy = utilities.get_plugin_function(program=i,
                                                     cmd='run',
                                                     import_path=IMPORT_PATH)
            logger.debug("Starting Strategy: %s", i)
            strategy()
