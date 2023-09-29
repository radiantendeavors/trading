"""!
@package pytrader.libs.contracts.abstractbase

Provides the Base Class for Contracts

@author G S Derber
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


@file pytrader/libs/contracts/__init__.py

Provides the Base Class for Contracts
"""
# System libraries
from datetime import date, datetime, timedelta
from multiprocessing import Queue
from time import sleep
from typing import Optional

# 3rd Party libraries
from ibapi.contract import Contract as IbContract

# Application Libraries
from pytrader.libs.contracts.abstractbase import AbstractBaseContract
from pytrader.libs.system import logging

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The base logger.
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IndOptionContract(AbstractBaseContract):
    """!
    The AbstractBaseContract Class.
    """
    sec_type = "OPT"

    def create_contract(self,
                        exchange: str = "SMART",
                        currency: str = "USD",
                        expiry: Optional[str] = None,
                        right: Optional[str] = None,
                        strike: Optional[float] = None,
                        multiplier: Optional[int] = 100) -> None:
        """!
        Creates a minimal contract that can be used to query the broker for further details.

        @param sec_type: Type of security
        @param exchange: Trading Exchange
        @param currency: Currency
        @param expiry: Options / Futures Expiration Date
        @param strike: Options Strike Price.
        @param right: Options right (Call or Put).

        @return None
        """
        self.contract.exchange = exchange
        self.contract.currency = currency
        self.contract.lastTradeDateOrContractMonth = expiry
        self.contract.multiplier = multiplier
        self.contract.right = right
        self.contract.strike = strike
        #self.contract.localSymbol =

        return self._gen_option_contract_name(expiry, right, strike)

    def get_contract_details(self, sender: str = "downloader") -> None:
        self.req_contract_details(sender)
        sleep(1)

    def select_columns(self):
        self.columns = {
            "contract": [
                self.contract.conId, self.contract.symbol, self.contract.secType,
                self.contract.exchange, self.contract.currency, self.contract.localSymbol,
                self.contract.primaryExchange, self.contract.tradingClass
            ]
        }

    def add_details_columns(self):
        self.columns["details"] = [
            self.id, self.details.marketName, self.details.minTick, self.details.priceMagnifier,
            self.details.validExchanges, self.details.longName, self.details.industry,
            self.details.category, self.details.subcategory, self.details.timeZoneId,
            self.details.stockType, self.details.aggGroup
        ]

    def _gen_option_contract_name(self, expiry: str, right: str, strike: float) -> str:
        strike_left = str(strike).split(".", maxsplit=1)[0]
        strike_right = str(strike).split(".")[1]

        strike_str = strike_left.rjust(5, "0") + strike_right.ljust(3, "0")
        local_symbol = self.contract.symbol.ljust(6, " ")
        option_name = local_symbol + expiry[-6:] + right[0] + strike_str
        return option_name
