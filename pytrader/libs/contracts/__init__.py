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
from datetime import date, datetime, timedelta
from multiprocessing import Queue
from typing import Optional

# 3rd Party libraries
from ibapi.contract import Contract as IbContract

# Application Libraries
from pytrader.libs.clients.database.mysql.ibkr.etf_contracts import (
    IbkrEtfContractDetails, IbkrEtfContracts, IbkrEtfExchanges,
    IbkrEtfHistoryBeginDate, IbkrEtfLiquidHours, IbkrEtfOrderTypes,
    IbkrEtfTradingHours)
from pytrader.libs.clients.database.mysql.ibkr.index_contracts import (
    IbkrIndexContractDetails, IbkrIndexContracts, IbkrIndexExchanges,
    IbkrIndexHistoryBeginDate, IbkrIndexLiquidHours, IbkrIndexOrderTypes,
    IbkrIndexTradingHours)
from pytrader.libs.clients.database.mysql.ibkr.stock_contracts import (
    IbkrStockContractDetails, IbkrStockContracts, IbkrStockExchanges,
    IbkrStockHistoryBeginDate, IbkrStockLiquidHours, IbkrStockOrderTypes,
    IbkrStockTradingHours)
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

    def __init__(self,
                 ticker: Optional[str],
                 sec_type: Optional[str],
                 contract: Optional[IbContract] = None) -> None:
        """!
        Creates a contract
        """
        if contract:
            self.contract = contract
            self.sec_type = None

        else:
            self.contract = IbContract()
            self.contract.symbol = ticker

            # We keep the initial security type because that determines which database table to
            # query.  IBKR combines STK and ETF.  But we need to keep them separate.
            self.sec_type = sec_type
            self.contract.secType = self._sanitize_security_type()

        self.details = None

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

    def _set_complex_contract_details(self,
                                      expiry: str,
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


class DBContract(BaseContract):

    def __init__(self,
                 ticker: Optional[str],
                 sec_type: Optional[str],
                 contract: Optional[IbContract] = None):
        super().__init__(ticker, sec_type, contract)
        self.id = 0

    def query_contract_details(self) -> list | tuple:
        db = self._select_contract_class()
        criteria = {"ticker_symbol": [self.contract.symbol]}
        raw_results = db.select(criteria=criteria)

        if raw_results:
            results = raw_results[0]
            logger.debug("Results: %s", results)
            self.id = results["id"]
            logger.debug("Id: %s", self.id)
            return results

        return False

    def query_history_begin_date(self) -> list | tuple:
        db = self._select_history_begin_date_class()
        criteria = {"ibkr_contract_id": [self.id]}
        results = db.select(criteria=criteria)

        return results

    def save_contract(self, details) -> None:
        logger.debug("Saving Contract")
        self.details = details

        if details.contract.secType == "IND":
            self.sec_type = "IND"
        elif details.contract.secType == "STK":
            self.sec_type = details.stockType

        contract_db = self._select_contract_class()

        logger.debug("Contract Info Received")
        logger.debug("Contract ID: %s", details.contract.conId)
        logger.debug("Symbol: %s", details.contract.symbol)
        logger.debug("Security Type: %s", details.contract.secType)
        logger.debug("LastTradeDate: %s", details.contract.lastTradeDateOrContractMonth)
        logger.debug("Strike: %s", details.contract.strike)
        logger.debug("Right: %s", details.contract.right)
        logger.debug("Multiplier: %s", details.contract.multiplier)
        logger.debug("Exchange: %s", details.contract.exchange)
        logger.debug("Currency: %s", details.contract.currency)
        logger.debug("Local Symbol: %s", details.contract.localSymbol)
        logger.debug("Primary Exchange: %s", details.contract.primaryExchange)
        logger.debug("Trading Class: %s", details.contract.tradingClass)
        logger.debug("Security ID Type: %s", details.contract.secIdType)
        logger.debug("Security ID: %s", details.contract.secId)
        # logger.debug("Description: %s", details.contract.description)
        # logger.debug("Issuer Id: %s", details.contract.issuerId)

        logger.debug("Contract Detail Info")
        logger.debug("Market name: %s", details.marketName)
        logger.debug("Min Tick: %s", details.minTick)
        logger.debug("Price Magnifier: %s", details.priceMagnifier)
        logger.debug("OrderTypes: %s", details.orderTypes)
        logger.debug("Valid Exchanges: %s", details.validExchanges)
        logger.debug("Underlying Contract ID: %s", details.underConId)
        logger.debug("Long name: %s", details.longName)
        logger.debug("Contract Month: %s", details.contractMonth)
        logger.debug("Industry: %s", details.industry)
        logger.debug("Category: %s", details.category)
        logger.debug("Subcategory: %s", details.subcategory)
        logger.debug("Time Zone: %s", details.timeZoneId)
        logger.debug("Trading Hours: %s", details.tradingHours)
        logger.debug("Liquid Hours: %s", details.liquidHours)
        logger.debug("EvRule: %s", details.evRule)
        logger.debug("EvMultiplier: %s", details.evMultiplier)
        logger.debug("AggGroup: %s", details.aggGroup)
        logger.debug("SecIdList: %s", details.secIdList)
        logger.debug("Underlying Symbol: %s", details.underSymbol)
        logger.debug("Underlying SecType: %s", details.underSecType)
        logger.debug("Market Rule Ids: %s", details.marketRuleIds)
        # logger.debug("Real Expiration Date: %s", details.RealExpirationDate)
        logger.debug("Last Trade Time: %s", details.lastTradeTime)
        logger.debug("Stock Type: %s", details.stockType)
        # logger.debug("Cusip: %s", details.cusip)
        # logger.debug("Ratings: %s", details.ratings)
        # logger.debug("DescAppend: %s", details.descAppend)
        # logger.debug("Bond Type: %s", details.bondType)
        # logger.debug("Coupon Type: %s", details.couponType)
        logger.debug("Next Option Date: %s", details.nextOptionDate)
        logger.debug("Details: %s", details)

        columns = self._select_columns()
        contract_db.insert(columns["contract"])

        self.query_contract_details()
        columns = self._select_columns()

        details_db = self._select_contract_details_class()
        logger.debug("Id: %s", self.id)
        details_db.insert(columns["details"])

        exchange_db = self._select_exchange_class()
        exchange_list = details.validExchanges.split(",")

        for exchange in exchange_list:
            logger.debug("Exchange: %s", exchange)
            exchange_db.insert([self.id, exchange])

    def save_history_begin_date(self, history_begin_date):
        logger.debug("History Begin Date: %s", history_begin_date)
        begin_dt = datetime.strptime(history_begin_date, "%Y%m%d  %H:%M:%S")
        begin_date_db = self._select_history_begin_date_class()
        begin_date_db.insert([self.id, begin_dt])

    def save_option_parameters(self, option_parameters):
        logger.debug("Option Parameters: %s", option_parameters)

    def _select_columns(self):
        match self.sec_type:
            case "ETF":
                return self._select_etf_columns()
            case "STK" | "COMMON":
                return self._select_stock_columns()
            case "IND":
                return self._select_index_columns()

    def _select_etf_columns(self):
        columns = {
            "contract": [
                self.contract.conId, self.contract.symbol, self.contract.secType,
                self.contract.exchange, self.contract.currency, self.contract.localSymbol,
                self.contract.primaryExchange, self.contract.tradingClass
            ],
            "details": [
                self.id, self.details.marketName, self.details.minTick,
                self.details.priceMagnifier, self.details.longName, self.details.timeZoneId,
                self.details.stockType, self.details.aggGroup
            ]
        }
        return columns

    def _select_stock_columns(self):
        columns = {
            "contract": [
                self.contract.conId, self.contract.symbol, self.contract.secType,
                self.contract.exchange, self.contract.currency, self.contract.localSymbol,
                self.contract.primaryExchange, self.contract.tradingClass
            ],
            "details": [
                self.id, self.details.marketName, self.details.minTick,
                self.details.priceMagnifier, self.details.longName, self.details.industry,
                self.details.category, self.details.subcategory, self.details.timeZoneId,
                self.details.stockType, self.details.aggGroup
            ]
        }
        return columns

    def _select_index_columns(self):
        columns = {
            "contract": [
                self.contract.conId, self.contract.symbol, self.contract.secType,
                self.contract.exchange, self.contract.currency, self.contract.localSymbol
            ],
            "details": [
                self.id, self.details.marketName, self.details.minTick,
                self.details.priceMagnifier, self.details.longName, self.details.industry,
                self.details.category, self.details.subcategory, self.details.timeZoneId,
                self.details.aggGroup
            ]
        }
        return columns

    def _select_contract_class(self):
        match self.sec_type:
            case "ETF":
                return IbkrEtfContracts()
            case "STK" | "COMMON":
                return IbkrStockContracts()
            case "IND":
                return IbkrIndexContracts()

    def _select_contract_details_class(self):
        match self.sec_type:
            case "ETF":
                return IbkrEtfContractDetails()
            case "STK" | "COMMON":
                return IbkrStockContractDetails()
            case "IND":
                return IbkrIndexContractDetails()

    def _select_history_begin_date_class(self):
        match self.sec_type:
            case "ETF":
                return IbkrEtfHistoryBeginDate()
            case "STK" | "COMMON":
                return IbkrStockHistoryBeginDate()
            case "IND":
                return IbkrIndexHistoryBeginDate()

    def _select_exchange_class(self):
        match self.sec_type:
            case "ETF":
                return IbkrEtfExchanges()
            case "STK" | "COMMON":
                return IbkrStockExchanges()
            case "IND":
                return IbkrIndexExchanges()


class Contract(DBContract):
    """!
    Manages Contract Information.
    """

    def __init__(self,
                 queue: Queue,
                 ticker: Optional[str] = "",
                 sec_type: Optional[str] = "",
                 contract: Optional[IbContract] = None):
        super().__init__(ticker, sec_type, contract)
        self.queue = queue
        self.local_queue = queue

    def set_local_queue(self, queue: Queue) -> None:
        self.local_queue = queue

    def get_contract_details(self, sender: str = "downloader") -> None:
        db_contract = self.query_contract_details()

        if db_contract:
            oldest_allowed_date = date.today() - timedelta(days=7)
            last_updated = db_contract["last_updated"]
            if last_updated < oldest_allowed_date:
                logger.debug("Too Old! Last Updated: %s", last_updated)
                self.req_contract_details(sender)
            else:
                logger.debug("Last Updated: %s", last_updated)
                self.contract.conId = db_contract["contract_id"]
                self.contract.exchange = db_contract["exchange"]
                self.contract.currency = db_contract["currency"]
                self.contract.localSymbol = db_contract["local_symbol"]

                if self.sec_type in ["ETF", "STK"]:
                    self.contract.primaryExchange = db_contract["primary_exchange"]
                    self.contract.tradingClass = db_contract["trading_class"]

                self.local_queue.put("Done")
        else:
            msg = "Contract Details are not in the database, requesting details from broker."
            logger.debug(msg)
            self.req_contract_details(sender)

    def get_contract_history_begin_date(self, sender: str = "downloader") -> None:
        # Ensure we have set self.id
        self.query_contract_details()

        raw_results = self.query_history_begin_date()

        if raw_results:
            db_history_begin_date = raw_results[0]

            # This updates VERY rarely
            oldest_allowed_date = date.today() - timedelta(days=90)
            last_updated = db_history_begin_date["last_updated"]
            if last_updated < oldest_allowed_date:
                logger.debug("Too Old! Last Updated: %s", last_updated)
                self.req_contract_details(sender)
            else:
                self.local_queue.put("Done")
        else:
            self.req_contract_history_begin_date(sender)

    def get_contract_option_parameters(self, sender: str = "downloader") -> None:
        self.req_contract_option_parameters(sender)

    def req_contract_details(self, sender: str) -> None:
        """!
        Sends a contract to the broker

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

    def req_contract_option_parameters(self, sender: str) -> None:
        """!
        Requests History Begin Date from the broker.

        @param sender: identifies who is sending the request.

        @return None
        """
        message = {sender: {"req": {"option_details": self.contract}}}
        self.queue.put(message)
