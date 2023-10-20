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
class StrategyMarketDataObserver(MarketDataObserver):
    """!
    Strategy observer for streaming market data.
    """

    def update(self, subject: Subject) -> None:
        """!
        Sends market data to the Strategy Processes

        @param subject:

        @return None:
        """
        if len(self.tickers) > 0:
            if subject.ticker in self.tickers:
                message = {"market_data": {subject.ticker: subject.market_data}}
                self.msg_queue.put(message)


class StrategyOrderDataObserver(OrderDataObserver):
    """!
    Strategy observer for order status updates.
    """

    def update(self, subject: Subject) -> None:
        """!
        Sends order status updates to the strategy

        @param subject:

        @return None
        """
        if len(self.order_ids) > 0:
            if subject.order_id in self.order_ids:
                message = {"order_status": subject.order_status}
                self.msg_queue.put(message)


class StrategyRealTimeBarObserver(RealTimeBarObserver):
    """!
    Strategy observer for Real time bar data.
    """

    def update(self, subject: Subject) -> None:
        """!
        Sends real time bar data to the strategies.

        @param subject:

        @return None
        """
        if subject.ticker in self.tickers:
            msg = {"real_time_bars": {subject.ticker: {"rtb": subject.ohlc_bar}}}
            self.msg_queue.put(msg)
