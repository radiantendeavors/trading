"""!
@package pytrader.libs.applications.broker.observers.base

Provides the observer classes for Interactive Brokers TWS

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

@file pytrader/libs/applications/broker/observers/base.py
"""
# System Libraries
import multiprocessing
import queue

from pytrader.libs.events import ContractData, Observer, Subject
# Application Libraries
from pytrader.libs.system import logging

# 3rd Party Libraries

# Conditional Libraries

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
class BarDataObserver(Observer):
    """!
    Provides the bar data observer class.
    """

    def __init__(self, msg_queue: multiprocessing.Queue) -> None:
        self.ticker_bar_sizes = {}
        self.msg_queue = msg_queue

    def add_ticker_bar_sizes(self, tickers: list, bar_sizes: list) -> None:
        """!
        Adds ticker to bar sizes for observation.

        @param tickers:
        @param bar_sizes:

        @return None:
        """
        for ticker in tickers:
            if ticker not in list(self.ticker_bar_sizes):
                self.ticker_bar_sizes[ticker] = {}

            for bar_size in bar_sizes:
                if bar_size not in list(self.ticker_bar_sizes[ticker]):
                    self.ticker_bar_sizes[ticker][bar_size] = False


class ContractDataObserver(Observer):
    """!
    Provides an observer for Contract Data.
    """

    def __init__(self, msg_queue: multiprocessing.Queue):
        self.msg_queue = msg_queue


class ContractHistoryBeginObserver(Observer):
    """!
    Provides an observer for contract history begin date information.
    """

    def __init__(self, msg_queue: multiprocessing.Queue):
        self.msg_queue = msg_queue


class ContractOptionParameterObserver(Observer):
    """!
    Provides an observer for contract option parameters.
    """

    def __init__(self, msg_queue: multiprocessing.Queue):
        self.msg_queue = msg_queue


class MarketDataObserver(Observer):
    """!
    Provides an observer for streaming market data.
    """

    def __init__(self, msg_queue: multiprocessing.Queue):
        self.tickers = []
        self.msg_queue = msg_queue

    def add_tickers(self, tickers: list) -> None:
        """!
        Add tickers to list for observation.

        @param tickers:

        @return None
        """
        for ticker in tickers:
            if ticker not in self.tickers:
                self.tickers.append(ticker)


class OrderDataObserver(Observer):
    """!
    Provides an observer for orders.
    """

    def __init__(self, msg_queue: multiprocessing.Queue):
        self.order_ids = []
        self.msg_queue = msg_queue

    def add_order_id(self, order_id: int) -> None:
        """!
        Adds order id to order_ids for observation.

        @param order_id:

        @return None
        """
        if order_id not in self.order_ids:
            self.order_ids.append(order_id)


class OrderIdObserver(Observer):
    """!
    Provides an observer for tracking the next available order id.
    """

    def __init__(self, msg_queue: queue.Queue):
        self.msg_queue = msg_queue


class RealTimeBarObserver(Observer):
    """!
    Provides an observer for real time bar data.
    """

    def __init__(self, msg_queue: multiprocessing.Queue):
        self.tickers = []
        self.msg_queue = msg_queue

    def add_tickers(self, tickers: list) -> None:
        """!
        Add tickers to list of tickers for tracking real time bar data.
        """
        for ticker in tickers:
            if ticker not in self.tickers:
                self.tickers.append(ticker)
