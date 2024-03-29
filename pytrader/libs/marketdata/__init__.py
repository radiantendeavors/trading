"""!@package pytrader.libs.marketdata

Provides real-time market data

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


@file pytrader/libs/market/__init__.py
"""
# Standard libraries

# 3rd Party libraries
import pandas

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class BasicMktData():
    """!
    Contains bar history for a security
    """

    def __init__(self, *args, **kwargs):
        """!
        Initializes the class

        @param args -
        @param kwargs -

        @return None
        """

        ## Data Frame used to hold bar history.
        self.market_data = pandas.DataFrame()

        ## List to hold bar history in list format
        self.market_data_list = []

        logger.debug10("End Function")

    def append_tick(self, tick: list):
        self.market_data_list.append(tick)

    def get_ticks(self):
        return self.market_data


class MarketData(BasicMktData):
    pass
