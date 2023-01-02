"""!
@package pytrader.libs.securities

Provides the Base Class for Securities

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


@file pytrader/libs/securities/__init__.py
"""
# System libraries

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs import indexes
from pytrader.libs.securities import etfs, stocks

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)
min_sleeptime = 61
max_sleeptime = 121


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Securities():

    def __new__(cls, *args, **kwargs):
        securities_type = kwargs["securities_type"]
        subclass_map = {
            "etfs": etfs.Etfs,
            "stocks": stocks.Stocks,
            "indexes": indexes.Indexes
        }

        logger.debug("Subclass Map: %s", subclass_map)
        logger.debug("Securities Type: %s", securities_type)
        logger.debug("Securities Subclass: %s",
                     subclass_map.get(securities_type))

        subclass = subclass_map.get(securities_type)
        return subclass(*args, **kwargs)
