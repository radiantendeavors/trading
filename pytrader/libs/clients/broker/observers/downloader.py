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
from pytrader.libs.clients.broker.observers.base import (
    BarDataObserver, ContractDataObserver, ContractHistoryBeginObserver,
    ContractOptionParameterObserver, MarketDataObserver, OrderDataObserver,
    OrderIdObserver, RealTimeBarObserver)
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
        if subject.contract == "Error":
            msg = "Done"
        else:
            msg = {"contract_details": subject.contract}

        self.msg_queue.put(msg)


class DownloaderContractHistoryBeginObserver(ContractHistoryBeginObserver):

    def update(self, subject: Subject) -> None:
        logger.debug(subject)
        ticker = subject.history_begin_ids[subject.req_id]
        history_begin_date = subject.history_begin_date[subject.req_id]
        msg = {"contract_history_begin_date": {ticker: history_begin_date}}
        self.msg_queue.put(msg)


class DownloaderContractOptionParametersObserver(ContractOptionParameterObserver):

    def update(self, subject: Subject) -> None:
        ticker = subject.req_ids[subject.req_id]
        opt_params = subject.option_parameters[subject.req_id]
        msg = {"contract_option_parameters": {ticker: opt_params}}
        self.msg_queue.put(msg)


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


class DownloaderOrderIdObserver(OrderIdObserver):
    """!
    Observer for historical bar data.
    """

    def update(self, subject: Subject) -> None:
        """!
        Saves the historical bar data to the database.
        """
        msg = {"next_order_id": subject.order_id}
        self.msg_queue.put(msg)


class DownloaderRealTimeBarObserver(RealTimeBarObserver):

    def update(self, subject: Subject) -> None:
        if subject.ticker in self.tickers:
            msg = {"real_time_bars": {subject.ticker: {"rtb": subject.ohlc_bar}}}
            self.msg_queue.put(msg)
