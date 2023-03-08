"""!
@package pytrader.strategies.example_strategy

Provides an Example Strategy

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

@file pytrader/strategies/example_strategy/__init__.py

Provides an Example Strategy

"""
# System libraries
import datetime
import time
# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
#from pytrader.libs.securities import security
from pytrader import strategies
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
class Strategy(strategies.Strategy):

    def __init__(self, brokerclient):
        self.security = "IWM"
        self.bar_sizes = "5 secs"
        self.short_period = 5
        self.long_period = 20

        super().__init__(brokerclient)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def run(brokerclient):
    logger.debug10("Begin Function")
    strategy = Strategy(brokerclient)

    strategy.run()
    logger.debug("End Function")
