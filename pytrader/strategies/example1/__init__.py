"""!
@package pytrader.strategies.example1

Provides an Example Strategy

@author Geoff S. Derber
@version HEAD
@date 2022
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

@file pytrader/strategies/example_strategy/__init__.py

Provides an Example Strategy

"""
# System libraries
import datetime
import time

# 3rd Party libraries
from ibapi import order

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
#from pytrader.libs.securities import security
from pytrader import strategies
# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

@var colortext
Allows Color text on the console
"""
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Strategy(strategies.Strategy):

    def __init__(self, brokerclient):
        self.security = "IWM"
        self.bar_sizes = "1 min"
        self.short_period = 3
        self.long_period = 8

        super().__init__(brokerclient)

    def on_bar(self):
        short_name = str(self.short_period) + "EMA"
        self.bars_df[short_name] = self.bars_df["Close"].ewm(
            span=self.short_period, adjust=False).mean()

        long_name = str(self.long_period) + "EMA"
        self.bars_df[long_name] = self.bars_df["Close"].ewm(
            span=self.long_period, adjust=False).mean()

        logger.debug("Real Time Bar (with EMA): %s", self.bars_df.tail(20))

        previous_short = self.bars_df[short_name].iloc[-2]
        previous_long = self.bars_df[long_name].iloc[-2]

        current_short = self.bars_df[short_name].iloc[-1]
        current_long = self.bars_df[long_name].iloc[-1]

        cross_down = ((current_short <= current_long) &
                      (previous_short >= previous_long))

        cross_up = ((current_short >= current_long) &
                    (previous_short <= previous_long))
        logger.debug("Cross Up: %s", cross_up)
        logger.debug("Cross Down: %s", cross_down)

        quantity = 100

        if cross_up:
            logger.info("EMA Cross Up")

            if self.position_status == -1:
                quantity = quantity * 2

            buy_order = order.Order()
            buy_order.action = "BUY"
            buy_order.totalQuantity = quantity
            buy_order.orderType = "MKT"
            self.brokerclient.place_order(self.contract, buy_order)
            self.position_status = 1

        if cross_down:
            logger.info("EMA Cross Down")
            if self.position_status == 1:
                quantity = quantity * 2

            sell_order = order.Order()
            sell_order.action = "SELL"
            sell_order.totalQuantity = quantity
            sell_order.orderType = "MKT"
            self.brokerclient.place_order(self.contract, sell_order)
            self.position_status = -1


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def run(brokerclient):
    logger.debug10("Begin Function")
    strategy = Strategy(brokerclient)

    strategy.run()
    logger.debug("End Function")
