"""!
@package pytrader.libs.contracts

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
from datetime import date, timedelta
from multiprocessing import Queue
from typing import Optional

# 3rd Party libraries
from ibapi import contract

# Application Libraries
from pytrader.libs.clients.database.mysql.ibkr.etf_contracts import IbkrEtfContracts
from pytrader.libs.clients.database.mysql.ibkr.index_contracts import IbkrIndContracts
from pytrader.libs.clients.database.mysql.ibkr.option_contracts import IbkrOptContracts
from pytrader.libs.clients.database.mysql.ibkr.stock_contracts import IbkrStkContracts
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
class BaseContract():
    """!
    The Base Contract Class
    """

    def __init__(self, queue: Queue, ticker: str, sec_type: str):
        """!
        Creates a contract
        """
        self.queue = queue
        self.contract = contract.Contract()
        self.contract.symbol = ticker

        # We keep the initial security type because that determines which database table to query.
        # IBKR combines STK and ETF.  But we need to keep them separate.
        self.sec_type = sec_type
        self.contract.secType = self._sanitize_security_type()

    def create_contract(self,
                        exchange: str = "SMART",
                        currency: str = "USD",
                        expiry: Optional[str] = None,
                        right: Optional[str] = None,
                        strike: Optional[float] = None) -> None:
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

        if expiry and self.contract.secType in ['OPT', 'FUT', 'FUTOPT', 'WAR']:
            self._set_complex_contract_details(expiry, right, strike)
            self.contract.localSymbol = self._gen_option_contract_name(expiry, right, strike)
        else:
            self.contract.localSymbol = self.contract.symbol

    def _gen_option_contract_name(self, expiry: str, right: str, strike: float) -> str:
        strike_left = str(strike).split(".", maxsplit=1)[0]
        strike_right = str(strike).split(".")[1]

        strike_str = strike_left.rjust(5, "0") + strike_right.ljust(3, "0")
        local_symbol = self.contract.symbol.ljust(6, " ")
        option_name = local_symbol + expiry[-6:] + right[0] + strike_str
        return option_name

    def _set_complex_contract_details(self, expiry: str,
                                      right: Optional[str] = None,
                                      strike: Optional[str] = None) -> None:
        """!
        Sets contract details for more complex contracts: Options, Futures, Future Options, and
        Warrants.

        @param expiry:
        @param right:
        @param strike:

        @return None
        """
        self.contract.lastTradeDateOrContractMonth = expiry

        match self.contract.secType:
            case "OPT":
                self.contract.multiplier = "100"
                self.contract.strike = strike
                self.contract.right = right
            case _:
                logger.warning("Settings for Security Type '%s' have not been implemented.",
                               self.contract.secType)

    def _sanitize_security_type(self) -> str:
        """!
        Sanitizes the security type.  The format of the security type from webscraping the contract
        universe does not match the format required by the API.  This ensures that the security type
        is the correct type for the API.

        @param sec_type: Input Security Type

        @return sec_type: Sanitized Security Type
        """
        match self.sec_type:
            case "ETF":
                return "STK"
            case "OPTGRP":
                return "OPT"
            case "FUTGRP":
                return "FUT"
            case _:
                logger.debug9("No changes to make for Security Type '%s'", self.sec_type)
                return self.sec_type


class Contract(BaseContract):
    """!
    Manages Contract Information.
    """

    def get_contract_details(self, sender: str = "downloader") -> None:
        db_contract = self.query_contract_details()

        if db_contract:
            oldest_allowed_date = date.today() - timedelta(days=7)
            last_updated = db_contract[0]["last_updated"]
            if last_updated < oldest_allowed_date:
                logger.debug("Too Old! Last Updated: %s", last_updated)
                self.req_contract_details(sender)
            else:
                logger.debug("Last Updated: %s", last_updated)

            self.contract.exchange = db_contract[0]["exchange"]
            self.contract.currency = db_contract[0]["currency"]
            self.contract.localSymbol = db_contract[0]["local_symbol"]

            if self.sec_type in ["ETF", "STK"]:
                self.contract.primaryExchange = db_contract[0]["primary_exchange"]
                self.contract.tradingClass = db_contract[0]["trading_class"]
        else:
            msg = "Contract Details are not in the database, requesting details from broker."
            logger.debug(msg)
            self.req_contract_details(sender)

    def get_contract_history_begin_date(self, sender: str = "downloader") -> None:
        self.req_contract_history_begin_date(sender)

    def query_contract_details(self) -> list | tuple:
        db = self._select_contract_class()
        criteria = {"ticker_symbol": [self.contract.symbol]}
        return db.select(criteria=criteria)

    def req_contract_details(self, sender: str) -> None:
        """!
        Sends a contract to the broker.

        @param sender: identifies who is sending the contract

        @return None"""
        message = {sender: {"req": {"contract_details": self.contract}}}
        self.queue.put(message)

    def req_contract_history_begin_date(self, sender: str) -> None:
        """!
        Requests History Begin Date from the broker.

        @param sender: identifies who is sending the request.

        @return None
        """
        message = {sender: {"req": {"history_begin_date": self.contract}}}
        self.queue.put(message)

    def _select_contract_class(self):
        match self.sec_type:
            case "ETF":
                return IbkrEtfContracts()
            case "STK":
                return IbkrStkContracts()
            case "OPT":
                return IbkrOptContracts()
            case "IND":
                return IbkrIndContracts()
