"""!
@package pytrader.libs.security

Provides the broker client

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


@file security.py
"""
# System libraries

# 3rd Party libraries
from ibapi.contract import Contract

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.indexes import index
from pytrader.libs.securities import etf
from pytrader.libs.securities import stock

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
class Security():

    def __new__(cls, *args, **kwargs):
        security_type = kwargs["security_type"]
        subclass_map = {
            "etfs": etf.Etf,
            "stocks": stock.Stock,
            "indexes": index.Index
        }

        logger.debug3("Subclass Map: %s", subclass_map)
        logger.debug2("Securities Type: %s", security_type)
        logger.debug2("Securities Subclass: %s",
                      subclass_map.get(security_type))

        subclass = subclass_map.get(security_type)
        return subclass(*args, **kwargs)
