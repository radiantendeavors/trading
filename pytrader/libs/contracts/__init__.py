"""!@package pytrader.strategies

Provides the Base Class for a Strategy.

@author G S derber
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

@file pytrader/strategies/__init__.py

    Provides the Base Class for a Strategy

"""
# System libraries

# 3rd Party libraries
from ibapi import contract

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base Logger
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Contract(contract.Contract):

    def __init__(self, symbol, sec_type: str = "STK"):
        self.symbol = symbol
        self.secType = sec_type
        self.exchange = "SMART"
        self.currency = "USD"

        super().__init__()
