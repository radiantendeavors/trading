"""!
@package pytrader.libs.applications.broker.observers.strategy

Provides the observer classes for the running strategies

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

@file pytrader/libs/applications/broker/observers/strategy.py
"""
# System Libraries

# 3rd Party Libraries

# Other Application Libraries
from pytrader.libs.clients.broker.observers.base import (BarDataObserver,
                                                         ContractDataObserver,
                                                         MarketDataObserver,
                                                         OrderDataObserver,
                                                         RealTimeBarObserver)
from pytrader.libs.events import Subject
# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

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
class StrategyBarDataObserver(BarDataObserver):
    """!
    """

    def update(self, subject: Subject) -> None:
        for ticker, bar_sizes_dict in self.ticker_bar_sizes.items():
            for bar_size, sent_status in bar_sizes_dict.items():
                if not sent_status:

                    # Ensure we only send a bar size if it is available.
                    # Avoids KeyError for missing bar sizes.
                    if bar_size in list(subject.ohlc_bars[ticker]):
                        ohlc_bars = subject.ohlc_bars[ticker][bar_size]

                        msg = {"bars": {ticker: {bar_size: ohlc_bars}}}
                        self.msg_queue.put(msg)
                        self.ticker_bar_sizes[ticker][bar_size] = True


class StrategyContractDataObserver(ContractDataObserver):

    def update(self, subject: Subject) -> None:
        contracts = {}

        if len(self.tickers) > 0:
            for ticker in self.tickers:
                contracts[ticker] = subject.contracts[ticker]

            msg = {"contracts": contracts}
            self.msg_queue.put(msg)


class StrategyMarketDataObserver(MarketDataObserver):

    def update(self, subject: Subject) -> None:
        if len(self.tickers) > 0:
            if subject.ticker in self.tickers:
                message = {"market_data": {subject.ticker: subject.market_data}}
                self.msg_queue.put(message)


class StrategyOrderDataObserver(OrderDataObserver):

    def update(self, subject: Subject) -> None:
        if len(self.order_ids) > 0:
            if subject.order_id in self.order_ids:
                message = {"order_status": subject.order_status}
                self.msg_queue.put(message)


class StrategyRealTimeBarObserver(RealTimeBarObserver):

    def update(self, subject: Subject) -> None:
        if subject.ticker in self.tickers:
            msg = {"real_time_bars": {subject.ticker: {"rtb": subject.ohlc_bar}}}
            self.msg_queue.put(msg)
