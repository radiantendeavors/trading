"""!@package pytrader.libs.events.marketdata

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

@file pytrader/libs/events/marketdata.py
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
class MarketData(Subject):
    """!
    Market Data Subject
    """

    _observers: List[Observer] = []
    contracts = {}
    ticker = None
    market_data = {}
    rtmd_ids = {}

    def __init__(self):
        self.tickers = []
        self.brokerclient = None

    def add_tickers(self, tickers: list, contracts: dict) -> None:
        """!
        Adds tickers to tracker

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

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, modifier=None) -> None:
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)
