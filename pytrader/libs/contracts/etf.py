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
from typing import Optional

# 3rd Party libraries
from ibapi.contract import Contract as IbContract

# Application Libraries
from pytrader.libs.clients.database.mysql.ibkr.etf_contracts import (
    IbkrEtfContractDetails, IbkrEtfContracts, IbkrEtfHistoryBeginDate,
    IbkrEtfLiquidHours, IbkrEtfOptParams, IbkrEtfOrderTypes,
    IbkrEtfTradingHours)
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
class EtfContract(AbstractBaseContract):
    """!
    The EtfContract Class.
    """
    contract_table = IbkrEtfContracts()
    contract_details_table = IbkrEtfContractDetails()
    history_begin_date_table = IbkrEtfHistoryBeginDate()
    option_parameters_table = IbkrEtfOptParams()
    sec_type = "ETF"

    def create_contract(self,
                        exchange: str = "SMART",
                        currency: str = "USD",
                        expiry: Optional[str] = None,
                        right: Optional[str] = None,
                        strike: Optional[float] = None,
                        multiplier: Optional[int] = 0) -> None:
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
        self.contract.localSymbol = self.contract.symbol

        if expiry:
            logger.debug("Expiry Should not be set for ETF Contracts: %s", expiry)
        if right:
            logger.debug("Right Should not be set for ETF Contracts: %s", right)
        if strike:
            logger.debug("Expiry Should not be set for ETF Contracts: %s", strike)

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
            self.details.validExchanges, self.details.longName, self.details.timeZoneId,
            self.details.stockType, self.details.aggGroup
        ]
