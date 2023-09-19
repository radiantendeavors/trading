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

    def __init__(self, msg_queue: multiprocessing.Queue):
        self.ticker_bar_sizes = {}
        self.msg_queue = msg_queue

    def add_ticker_bar_sizes(self, tickers, bar_sizes):
        for ticker in tickers:
            if ticker not in list(self.ticker_bar_sizes):
                self.ticker_bar_sizes[ticker] = {}

            for bar_size in bar_sizes:
                if bar_size not in list(self.ticker_bar_sizes[ticker]):
                    self.ticker_bar_sizes[ticker][bar_size] = False


class ContractDataObserver(Observer):

    def __init__(self, msg_queue: multiprocessing.Queue):
        self.msg_queue = msg_queue


class ContractHistoryBeginObserver(Observer):

    def __init__(self, msg_queue: multiprocessing.Queue):
        self.msg_queue = msg_queue


class MarketDataObserver(Observer):

    def __init__(self, msg_queue: multiprocessing.Queue):
        self.tickers = []
        self.msg_queue = msg_queue

    def add_tickers(self, tickers):
        for ticker in tickers:
            if ticker not in self.tickers:
                self.tickers.append(ticker)


class OrderDataObserver(Observer):

    def __init__(self, msg_queue: multiprocessing.Queue):
        self.order_ids = []
        self.msg_queue = msg_queue

    def add_order_id(self, order_id):
        if order_id not in self.order_ids:
            self.order_ids.append(order_id)


class OrderIdObserver(Observer):

    def __init__(self, msg_queue: queue.Queue):
        self.msg_queue = msg_queue


class RealTimeBarObserver(Observer):

    def __init__(self, msg_queue: multiprocessing.Queue):
        self.tickers = []
        self.msg_queue = msg_queue

    def add_tickers(self, tickers):
        for ticker in tickers:
            if ticker not in self.tickers:
                self.tickers.append(ticker)
