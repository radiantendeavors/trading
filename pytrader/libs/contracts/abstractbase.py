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
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from multiprocessing import Queue
from typing import Optional
from zoneinfo import ZoneInfo

# 3rd Party libraries
from ibapi.contract import Contract as IbContract
from ibapi.contract import ContractDetails

# Application Libraries
from pytrader.libs.contracts.database import DatabaseContract
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
class AbstractBaseContract(DatabaseContract, ABC):
    """!
    The AbstractBaseContract Class.
    """

    def __init__(self,
                 queue: Queue,
                 local_queue: Queue,
                 ticker: Optional[str] = "",
                 contract: Optional[IbContract] = None):
        """!
        Creates an instance of an AbstractBaseContract class.

        @return None
        """
        super().__init__(ticker, contract)
        self.queue = queue
        self.local_queue = local_queue
        self.expirations = []
        self.strikes = []
        self.options_multiplier = None

    @abstractmethod
    def add_details_columns(self) -> None:
        """!
        Add details columns to the columns dictionary.
        """

    @abstractmethod
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

    def get_contract_details(self, sender: str = "downloader") -> None:
        """!
        Will set the contract details if they are available in the database.  Otherwise, it will
        request the contract details from the broker.

        @param sender:

        @return None
        """
        db_contract = self.query_contracts()

        if db_contract:
            self.id = db_contract["id"]

            # Available Trading / Liquid Hours only provides the the next 5 days.
            oldest_allowed_date = date.today() - timedelta(days=5)
            last_updated = db_contract["last_updated"]
            self.set_contract_parameters(db_contract)
            if last_updated < oldest_allowed_date:
                logger.debug("Too Old! Last Updated: %s", last_updated)
                self.req_contract_details(sender)
            else:
                logger.debug("Last Updated: %s", last_updated)
                self.local_queue.put("Next")
        else:
            msg = (f"Contract Details are not in the database for {self.contract.symbol}, "
                   f"requesting details from broker.")
            logger.debug(msg)
            self.req_contract_details(sender)

    def get_contract_history_begin_date(self, sender: str = "downloader") -> None:
        """!
        Queries the begin history date from the database.  If not available, it will request the
        information from the broker.

        @param sender:

        @return None
        """
        # Run query_contracts to ensure we have set self.id
        if self.sec_type == "OPT":
            additional_criteria = self._set_additional_criteria()
            self.query_contracts(additional_criteria)
        else:
            self.query_contracts()

        raw_results = self.query_history_begin_date()

        if raw_results:
            db_history_begin_date = raw_results[0]

            # This updates VERY rarely
            oldest_allowed_date = date.today() - timedelta(days=90)
            last_updated = db_history_begin_date["last_updated"]
            if last_updated < oldest_allowed_date:
                logger.debug("Too Old! Last Updated: %s", last_updated)
                self.req_contract_history_begin_date(sender)
            else:
                self.local_queue.put("Next")
        else:
            self.req_contract_history_begin_date(sender)

    def get_contract_option_parameters(self, sender: str = "downloader") -> None:
        self.query_contracts()

        raw_results = self.query_option_parameters()

        if raw_results:
            db_date = raw_results[0]

            expirations = []
            strikes = []

            oldest_allowed_date = date.today() - timedelta(days=7)
            last_updated = db_date["last_updated"]

            if last_updated < oldest_allowed_date:
                logger.debug("Too Old! Last Updated: %s", last_updated)
                self.req_contract_option_parameters(sender)
            else:
                for item in raw_results:
                    expirations = list(
                        map(str.strip, list(set(expirations + item["expirations"].split(",")))))
                    strikes = list(set(strikes + item["strikes"].split(",")))
                    self.options_multiplier = item["multiplier"]

                self.expirations = list(set(expirations))
                self.strikes = list(set(strikes))
                self.expirations.sort()
                self.strikes.sort()
                msg = {
                    "db_option_parameters":
                    [self.contract.symbol, self.expirations, self.strikes, self.options_multiplier]
                }
                self.local_queue.put(msg)
        else:
            self.req_contract_option_parameters(sender)

    def get_option_parameters(self) -> None:
        return (self.expirations, self.strikes, self.options_multiplier)

    def get_option_contract_parameters(self) -> None:
        return (self.contract.lastTradeDateOrContractMonth, self.contract.strike,
                self.contract.right)

    def req_contract_details(self, sender: str) -> None:
        """!
        Sends a contract to the broker

        @param sender: identifies who is sending the contract

        @return None"""
        message = {sender: {"req": {"contract_details": {self.local_symbol: self.contract}}}}
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

    def query_no_history(self):
        criteria = self._set_criteria()
        return self.no_history_table.select(criteria=criteria)

    @abstractmethod
    def query_invalid_contracts(self):
        """!
        Query Database for invalid contracts.
        """

    @abstractmethod
    def select_columns(self) -> None:
        """!
        Sets columns for contract table and contract details table.
        """

    def save_contract(self, details: ContractDetails) -> None:
        """!
        Saves Contract, Contract Details, to their respective tables.

        @param detail: Contract details to save (Contains the contract)

        @return None
        """

        self.contract = details.contract
        self.details = details
        self.sec_type = details.contract.secType

        self._log_contract()
        self._log_contract_details()

        self.select_columns()

        if self.contract.secType == "OPT":
            additional_criteria = self._set_additional_criteria()
            self.contract_table.insert(self.columns["contract"], additional_criteria)
            self.query_contracts(additional_criteria)
        else:
            self.contract_table.insert(self.columns["contract"])
            self.query_contracts()

        self.add_details_columns()
        self.contract_details_table.insert(self.columns["details"])

        self._save_contract_hours("liquid")
        self._save_contract_hours("trading")

    def save_invalid_contract(self):
        if self.sec_type == "OPT":
            columns = [
                self.contract.symbol, self.contract.lastTradeDateOrContractMonth,
                self.contract.strike, self.contract.right[0]
            ]
            additional_criteria = {
                "last_trading_date": [self.contract.lastTradeDateOrContractMonth],
                "strike": [self.contract.strike],
                "opt_right": [self.contract.right[0]],
            }

            self.invalid_contract_table.insert(columns, additional_criteria)

    def set_contract_parameters(self, db_contract):
        self.contract.conId = db_contract["contract_id"]
        self.contract.exchange = db_contract["exchange"]
        self.contract.currency = db_contract["currency"]
        self.contract.localSymbol = db_contract["local_symbol"]

        if self.sec_type in ["STK"]:
            self.contract.primaryExchange = db_contract["primary_exchange"]

        if self.sec_type in ["STK", "OPT"]:
            self.contract.tradingClass = db_contract["trading_class"]

        if self.sec_type in ["OPT"]:
            self.contract.lastTradeDateOrContractMonth = db_contract["last_trading_date"]
            self.contract.strike = db_contract["strike"]
            self.contract.right = db_contract["opt_right"]
            self.contract.multiplier = db_contract["multiplier"]

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _log_contract(self) -> None:
        logger.debug("Contract Info Received")
        logger.debug("Contract ID: %s", self.contract.conId)
        logger.debug("Symbol: %s", self.contract.symbol)
        logger.debug("Security Type: %s", self.contract.secType)
        logger.debug("LastTradeDate: %s", self.contract.lastTradeDateOrContractMonth)
        logger.debug("Strike: %s", self.contract.strike)
        logger.debug("Right: %s", self.contract.right)
        logger.debug("Multiplier: %s", self.contract.multiplier)
        logger.debug("Exchange: %s", self.contract.exchange)
        logger.debug("Currency: %s", self.contract.currency)
        logger.debug("Local Symbol: %s", self.contract.localSymbol)
        logger.debug("Primary Exchange: %s", self.contract.primaryExchange)
        logger.debug("Trading Class: %s", self.contract.tradingClass)
        logger.debug("Security ID Type: %s", self.contract.secIdType)
        logger.debug("Security ID: %s", self.contract.secId)
        if hasattr(self.contract, 'description'):
            logger.debug("Description: %s", self.contract.description)
        if hasattr(self.contract, 'issuerId'):
            logger.debug("Issuer Id: %s", self.contract.issuerId)

    def _log_contract_details(self) -> None:
        logger.debug("Contract Detail Info")
        logger.debug("Market name: %s", self.details.marketName)
        logger.debug("Min Tick: %s", self.details.minTick)
        logger.debug("Price Magnifier: %s", self.details.priceMagnifier)
        logger.debug("OrderTypes: %s", self.details.orderTypes)
        logger.debug("Valid Exchanges: %s", self.details.validExchanges)
        logger.debug("Underlying Contract ID: %s", self.details.underConId)
        logger.debug("Long name: %s", self.details.longName)
        logger.debug("Contract Month: %s", self.details.contractMonth)
        logger.debug("Industry: %s", self.details.industry)
        logger.debug("Category: %s", self.details.category)
        logger.debug("Subcategory: %s", self.details.subcategory)
        logger.debug("Time Zone: %s", self.details.timeZoneId)
        logger.debug("Trading Hours: %s", self.details.tradingHours)
        logger.debug("Liquid Hours: %s", self.details.liquidHours)
        logger.debug("EvRule: %s", self.details.evRule)
        logger.debug("EvMultiplier: %s", self.details.evMultiplier)
        logger.debug("AggGroup: %s", self.details.aggGroup)
        logger.debug("SecIdList: %s", self.details.secIdList)
        logger.debug("Underlying Symbol: %s", self.details.underSymbol)
        logger.debug("Underlying SecType: %s", self.details.underSecType)
        logger.debug("Market Rule Ids: %s", self.details.marketRuleIds)

        if hasattr(self.details, 'realExpirationDate'):
            logger.debug("Real Expiration Date: %s", self.details.realExpirationDate)

        logger.debug("Last Trade Time: %s", self.details.lastTradeTime)
        logger.debug("Stock Type: %s", self.details.stockType)

        if hasattr(self.details, 'cusip'):
            logger.debug("Cusip: %s", self.details.cusip)

        if hasattr(self.details, 'ratings'):
            logger.debug("Ratings: %s", self.details.ratings)

        if hasattr(self.details, 'descAppend'):
            logger.debug("DescAppend: %s", self.details.descAppend)

        if hasattr(self.details, 'bondType'):
            logger.debug("Bond Type: %s", self.details.bondType)

        if hasattr(self.details, 'couponType'):
            logger.debug("Coupon Type: %s", self.details.couponType)

        if hasattr(self.details, 'callable'):
            logger.debug("Callable: %s", self.details.callable)

        if hasattr(self.details, 'putable'):
            logger.debug("Putable: %s", self.details.putable)

        if hasattr(self.details, 'coupon'):
            logger.debug("Coupon: %s", self.details.coupon)

        if hasattr(self.details, 'convertible'):
            logger.debug("Convertable: %s", self.details.convertible)

        if hasattr(self.details, 'maturity'):
            logger.debug("Maturity: %s", self.details.maturity)

        if hasattr(self.details, 'nextOptionDate'):
            logger.debug("Next Option Date: %s", self.details.nextOptionDate)

        if hasattr(self.details, 'nextOptionType'):
            logger.debug("Next Option Type: %s", self.details.nextOptionType)

        if hasattr(self.details, 'nextOptionPartial'):
            logger.debug("Next Option Partial: %s", self.details.nextOptionPartial)

        if hasattr(self.details, 'notes'):
            logger.debug("Notes: %s", self.details.notes)

        if hasattr(self.details, 'minSize'):
            logger.debug("Min Size: %s", self.details.minSize)

        if hasattr(self.details, 'sizeIncrement'):
            logger.debug("Size Increment: %s", self.details.sizeIncrement)

        if hasattr(self.details, 'suggestedSizeIncrement'):
            logger.debug("Suggested Contract Size: %s", self.details.suggestedSizeIncrement)

    def _save_contract_hours(self, hours_type: str) -> None:
        if hours_type == "liquid":
            hours_list = self.details.liquidHours.split(";")
        elif hours_type == "trading":
            hours_list = self.details.tradingHours.split(";")

        for item in hours_list:
            if "CLOSED" not in item:
                item_list = item.split("-")
                begin = item_list[0]
                end = item_list[1]

                logger.debug("Begin Time: %s", begin)
                logger.debug("End Time: %s", end)

                begin_dt = datetime.strptime(
                    begin, "%Y%m%d:%H%M").replace(tzinfo=ZoneInfo(self.details.timeZoneId))
                end_dt = datetime.strptime(
                    end, "%Y%m%d:%H%M").replace(tzinfo=ZoneInfo(self.details.timeZoneId))

                if hours_type == "liquid":
                    self.contract_liquid_hours_table.insert([self.id, begin_dt, end_dt],
                                                            {"begin_dt": [begin_dt]})
                elif hours_type == "trading":
                    self.contract_trading_hours_table.insert([self.id, begin_dt, end_dt],
                                                             {"begin_dt": [begin_dt]})
