"""!@package pytrader.libs.events

The main user interface for the trading program.

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

@file pytrader/libs/events/__init__.py
"""
# System Libraries
from abc import ABC, abstractmethod
from threading import Event
from multiprocessing import Queue
from typing import List

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries

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
class Subject(ABC):

    @abstractmethod
    def attach(self, observer, brokerclient) -> None:
        """!
        Adds an observer for the Event.
        """

    @abstractmethod
    def detach(self, observer) -> None:
        """!
        Removes and observer from the subject
        """

    @abstractmethod
    def notify(self) -> None:
        """!
        Notifies all observers about an event.
        """


class Observer(ABC):
    """!
    The Observer interface declares the update method used by subjects.
    """

    @abstractmethod
    def update(self, subject: Subject) -> None:
        """!
        Receives an update from the subject.
        """


class BarData(Subject):

    _observers: List[Observer] = []
    contracts = {}
    ohlc_bars = {}

    def __init__(self):
        self.tickers = []
        self.bar_sizes = []
        self.brokerclient = None

    def add_bar_sizes(self, tickers: list, contracts: dict, bar_sizes: list):
        for ticker in tickers:
            if ticker not in self.tickers:
                self.tickers.append(ticker)

        for bar_size in bar_sizes:
            if bar_size not in self.bar_sizes:
                self.bar_sizes.append(bar_size)

        for ticker, contract_ in contracts.items():
            if ticker not in list(self.contracts.keys()):
                self.contracts[ticker] = contract_

    def attach(self, observer: Observer, brokerclient):
        self.brokerclient = brokerclient

        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)


class ContractData(Subject):

    _observers: List[Observer] = []
    contracts = {}

    def __init__(self):
        self.tickers = []
        self.brokerclient = None

    def add_tickers(self, tickers: list):
        for ticker in tickers:
            if ticker not in self.tickers:
                self.tickers.append(ticker)

    def attach(self, observer: Observer, brokerclient):
        self.brokerclient = brokerclient

        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def get_tickers(self):
        return self.tickers

    def get_contracts(self):
        return self.contracts

    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)


class MarketData(Subject):

    _observers: list[Observer] = []
    contracts = {}
    ticker = None
    market_data = {}
    rtmd_ids = {}

    def __init__(self):
        self.tickers = []
        self.brokerclient = None

    def add_tickers(self, tickers: list, contracts: dict):
        for ticker in tickers:
            if ticker not in self.tickers:
                self.tickers.append(ticker)

        for ticker, contract_ in contracts.items():
            if ticker not in list(self.contracts.keys()):
                self.contracts[ticker] = contract_

    def attach(self, observer: Observer, brokerclient):
        self.brokerclient = brokerclient
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)


class OptionData(Subject):

    _observers: List[Observer] = []
    option_details = {}
    contracts = {}

    def __init__(self):
        self.tickers = []
        self.brokerclient = None

    def add_tickers(self, tickers: list, contracts: dict):
        for ticker in tickers:
            if ticker not in self.tickers:
                self.tickers.append(ticker)

        for ticker, contract_ in contracts.items():
            if ticker not in list(self.contracts.keys()):
                self.contracts[ticker] = contract_

    def attach(self, observer: Observer, brokerclient):
        self.brokerclient = brokerclient

        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)


class OrderData(Subject):

    _observers: List[Observer] = []
    valid_order_ids = []
    order_id = None
    order_status = {}

    def __init__(self):
        self.brokerclient = None

    def attach(self, observer: Observer, brokerclient):
        self.brokerclient = brokerclient

        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)


class RealTimeBarData(Subject):
    _observers: List[Observer] = []
    contracts = {}
    rtb_ids = {}
    ohlc_bar = []
    tickers = []
    ticker = None

    def add_tickers(self, tickers: list, contracts: dict):
        for ticker in tickers:
            if ticker not in self.tickers:
                self.tickers.append(ticker)

        for ticker, contract_ in contracts.items():
            if ticker not in list(self.contracts.keys()):
                self.contracts[ticker] = contract_

    def attach(self, observer: Observer, brokerclient):
        self.brokerclient = brokerclient

        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)


class TickSubject(Subject):
    pass
