"""!@package pytrader.libs.events.bars

Provides Observers of Bar Data

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

@file pytrader/libs/events/bars.py
"""
from typing import List

from pytrader.libs.events.base import Observer, Subject
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
class BarData(Subject):
    """!
    Class for storing bar data
    """
    _observers: List[Observer] = []
    contracts = {}
    ohlc_bars = {}

    def __init__(self) -> None:
        """!
        Initializes the BarData class

        @return None
        """
        self.tickers = []
        self.bar_sizes = []
        self.brokerclient = None

    def add_bar_sizes(self, tickers: list, contracts: dict, bar_sizes: list) -> None:
        """!
        Add's bar sizes for monitoring.

        @param tickers:
        @param contacts
        @param bar_sizes:

        @return None
        """
        for ticker in tickers:
            if ticker not in self.tickers:
                self.tickers.append(ticker)

        for bar_size in bar_sizes:
            if bar_size not in self.bar_sizes:
                self.bar_sizes.append(bar_size)

        for ticker, contract_ in contracts.items():
            if ticker not in list(self.contracts):
                self.contracts[ticker] = contract_

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)


class RealTimeBarData(Subject):
    """!
    Class for storing real time bar data.
    """
    _observers: List[Observer] = []
    contracts = {}
    rtb_ids = {}
    ohlc_bar = []
    tickers = []
    ticker = None

    def add_tickers(self, tickers: list, contracts: dict):
        """!
        Add tickers to be tracked for real time bar data.

        @param tickers:
        @param contracts:


        @return None
        """
        for ticker in tickers:
            if ticker not in self.tickers:
                self.tickers.append(ticker)

        for ticker, contract_ in contracts.items():
            if ticker not in list(self.contracts):
                self.contracts[ticker] = contract_

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)
