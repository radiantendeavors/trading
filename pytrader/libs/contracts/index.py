"""!
@package pytrader.libs.contracts.index

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
from pytrader.libs.clients.database.mysql.ibkr.index_contracts import (
    IbkrIndexContractDetails, IbkrIndexContracts, IbkrIndexHistoryBeginDate,
    IbkrIndexLiquidHours, IbkrIndexNoHistory, IbkrIndexOptParams,
    IbkrIndexTradingHours)
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
class IndexContract(AbstractBaseContract):
    """!
    The IndexContract Class.
    """
    contract_table = IbkrIndexContracts()
    contract_details_table = IbkrIndexContractDetails()
    contract_liquid_hours_table = IbkrIndexLiquidHours()
    contract_trading_hours_table = IbkrIndexTradingHours()
    history_begin_date_table = IbkrIndexHistoryBeginDate()
    option_parameters_table = IbkrIndexOptParams()
    no_history_table = IbkrIndexNoHistory()
    sec_type = "IND"

    def __init__(self,
                 queue: Queue,
                 local_queue: Queue,
                 ticker: Optional[str] = "",
                 contract: Optional[IbContract] = None):
        super().__init__(queue, local_queue, ticker, contract)
        self.select_columns()

    def add_details_columns(self):
        self.columns["details"] = [
            self.id, self.details.marketName, self.details.minTick, self.details.priceMagnifier,
            self.details.longName, self.details.industry, self.details.category,
            self.details.subcategory, self.details.timeZoneId, self.details.evMultiplier,
            self.details.aggGroup, self.details.marketRuleIds
        ]

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

        self.local_symbol = self.contract.symbol

    def query_invalid_contracts(self):
        return None

    def select_columns(self):
        self.columns = {
            "contract": [
                self.contract.conId, self.contract.symbol, self.contract.secType,
                self.contract.exchange, self.contract.currency, self.contract.localSymbol
            ]
        }
