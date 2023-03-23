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

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
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

    def __init__(self):

        self.security = ["SPY", "QQQ", "IWM"]
        self.bar_sizes = ["5 mins", "1 hour"]
        self.short_period = 5
        self.long_period = 20
        self.quantity = 100
        self.use_options = False

        self.endtime = datetime.datetime.combine(
            datetime.date.today(), datetime.time(hour=15, minute=55))

        super().__init__()

    def continue_strategy(self):
        """!
        Checks various conditions for continuing to run the strategy

        @return True - if all conditions are True
        @return False - if any condition is False
        """
        logger.debug10("Begin Function")

        condition1 = (datetime.datetime.now() < self.endtime)

        logger.debug("Condition 1: %s", condition1)

        if condition1:
            return True
        else:
            return False

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

        self.next_option_contract = self.contract

        if cross_up:
            logger.info("EMA Cross Up")

            if len(self.short_position) > 0:
                self.close_short_position()

            self.open_long_position()

        if cross_down:
            logger.info("EMA Cross Down")

            if len(self.long_position) > 0:
                self.close_long_position()

            self.open_short_position()

    def on_end(self):
        self.brokerclient.req_global_cancel()
        if len(self.long_position) > 0:
            self.close_long_position()
        if len(self.short_position) > 0:
            self.close_short_position()


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def run():
    logger.debug10("Begin Function")
    strategy = Strategy()

    strategy.run()
    logger.debug("End Function")
