"""!
@package pytrader.libs.applications.broker.observers.downloader

Provides the observer classes for the DownloaderProcess

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

@file pytrader/libs/applications/broker/observers/downloader.py
"""
# System Libraries

# 3rd Party Libraries
from ibapi.contract import ContractDetails

# Application Libraries
from pytrader.libs.clients.broker.observers.base import (BarDataObserver,
                                                         ContractDataObserver,
                                                         ContractHistoryBeginObserver,
                                                         MarketDataObserver,
                                                         OrderDataObserver,
                                                         RealTimeBarObserver)
from pytrader.libs.clients.database.mysql.ibkr.etf_contracts import IbkrEtfContracts
from pytrader.libs.clients.database.mysql.ibkr.stock_contracts import IbkrStkContracts
from pytrader.libs.clients.database.mysql.ibkr.index_contracts import IbkrIndContracts
from pytrader.libs.events import Subject
from pytrader.libs.system import logging

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
class DownloaderBarDataObserver(BarDataObserver):
    """!
    Observer for historical bar data.
    """

    def update(self, subject: Subject) -> None:
        """!
        Saves the historical bar data to the database.
        """
        for ticker, bar_sizes_dict in self.ticker_bar_sizes.items():
            for bar_size, sent_status in bar_sizes_dict.items():
                if not sent_status:

                    # Ensure we only send a bar size if it is available.
                    # Avoids KeyError for missing bar sizes.
                    if bar_size in list(subject.ohlc_bars[ticker]):
                        ohlc_bars = subject.ohlc_bars[ticker][bar_size]

                        msg = {"bars": {ticker: {bar_size: ohlc_bars}}}
                        logger.debug("Historical Bars Received: %s", msg)


class DownloaderContractDataObserver(ContractDataObserver):

    def update(self, subject: Subject) -> None:
        """!
        Saves the historical bar data to the database.
        """
        details = subject.contract

        match details.contract.secType:
            case "STK":
                self._process_stock_details(details)
            case "IND":
                self._process_index_details(details)
            case "OPT":
                self._process_option_details(details)

    def _process_stock_details(self, details: ContractDetails) -> None:
        match details.stockType:
            case "ETF":
                self._process_etf_details(details)
            case "COMMON":
                self._process_common_details(details)

    def _process_common_details(self, details: ContractDetails) -> None:
        db = IbkrStkContracts()
        columns = [details.contract.conId, details.contract.symbol, details.contract.secType,
                   details.contract.exchange, details.contract.currency,
                   details.contract.localSymbol, details.contract.primaryExchange,
                   details.contract.tradingClass]
        db.insert(columns)
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
        logger.debug("Description: %s", details.contract.description)
        logger.debug("Issuer Id: %s", details.contract.issuerId)

    def _process_etf_details(self, details: ContractDetails) -> None:
        db = IbkrEtfContracts()
        columns = [details.contract.conId, details.contract.symbol, details.contract.secType,
                   details.contract.exchange, details.contract.currency,
                   details.contract.localSymbol, details.contract.primaryExchange,
                   details.contract.tradingClass]
        db.insert(columns)
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

    def _process_index_details(self, details: ContractDetails) -> None:
        db = IbkrIndContracts()
        columns = [details.contract.conId, details.contract.symbol, details.contract.secType,
                   details.contract.exchange, details.contract.currency,
                   details.contract.localSymbol]
        db.insert(columns)
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

    def _process_option_details(self, details: ContractDetails) -> None:
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

        logger.debug6("Contract Detail Info")
        logger.debug6("Market name: %s", details.marketName)
        logger.debug6("Min Tick: %s", details.minTick)
        logger.debug6("OrderTypes: %s", details.orderTypes)
        logger.debug6("Valid Exchanges: %s", details.validExchanges)
        logger.debug6("Underlying Contract ID: %s", details.underConId)
        logger.debug6("Long name: %s", details.longName)
        logger.debug6("Industry: %s", details.industry)
        logger.debug6("Category: %s", details.category)
        logger.debug6("Subcategory: %s", details.subcategory)
        logger.debug6("Time Zone: %s", details.timeZoneId)
        logger.debug6("Trading Hours: %s", details.tradingHours)
        logger.debug6("Liquid Hours: %s", details.liquidHours)
        logger.debug6("SecIdList: %s", details.secIdList)
        logger.debug6("Underlying Symbol: %s", details.underSymbol)
        logger.debug6("Stock Type: %s", details.stockType)
        logger.debug6("Next Option Date: %s", details.nextOptionDate)
        logger.debug6("Details: %s", details)


class DownloaderContractHistoryBeginObserver(ContractHistoryBeginObserver):

    def update(self, subject: Subject) -> None:
        logger.debug(subject)
        ticker = subject.history_begin_ids[subject.req_id]
        history_begin_date = subject.history_begin_date[subject.req_id]

        logger.debug("History Begin Date for %s: %s", ticker, history_begin_date)


class DownloaderMarketDataObserver(MarketDataObserver):

    def update(self, subject: Subject) -> None:
        if len(self.tickers) > 0:
            if subject.ticker in self.tickers:
                message = {"market_data": {subject.ticker: subject.market_data}}
                self.msg_queue.put(message)


class DownloaderOrderDataObserver(OrderDataObserver):

    def update(self, subject: Subject) -> None:
        if len(self.order_ids) > 0:
            if subject.order_id in self.order_ids:
                message = {"order_status": subject.order_status}
                self.msg_queue.put(message)


class DownloaderRealTimeBarObserver(RealTimeBarObserver):

    def update(self, subject: Subject) -> None:
        if subject.ticker in self.tickers:
            msg = {"real_time_bars": {subject.ticker: {"rtb": subject.ohlc_bar}}}
            self.msg_queue.put(msg)
