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
        self.bar_sizes = ["1 min"]
        self.short_period = 3
        self.long_period = 8
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

        cur_time = datetime.datetime.now()
        condition1 = (cur_time < self.endtime)
        logger.debug3("Curent Time: %s", cur_time)
        logger.debug3("End Time: %s", self.endtime)
        logger.debug2("Condition 1: %s", condition1)

        if condition1:
            return True
        else:
            return False

    def on_5sec_rtb(self, ticker, bar):
        logger.debug10("Begin Function")
        logger.debug("Run On 5sec RTB")
        logger.debug("Ticker: %s", ticker)
        logger.debug("Bar: %s", bar)
        logger.debug10("End Function")

    def on_ask(self, ticker, tick):
        logger.debug10("Begin Function")
        logger.debug("Run On Ask")
        logger.debug("Ticker: %s", ticker)
        logger.debug("Tick: %s", tick)
        logger.debug10("End Function")

    def on_bar(self, ticker, bar_size):
        self.bars[ticker][bar_size].create_dataframe()
        self.bars[ticker][bar_size].calculate_ema(self.short_period, "short")
        self.bars[ticker][bar_size].calculate_ema(self.long_period, "long")

        self.bars[ticker][bar_size].print_bar()
        cross_up = self.bars[ticker][bar_size].is_cross_up()
        cross_down = self.bars[ticker][bar_size].is_cross_down()

        if cross_up:
            logger.info("EMA Cross Up for ticker: %s", ticker)

            # if len(self.short_position) > 0:
            #     self.close_short_position()

            # self.open_long_position()

        if cross_down:
            logger.info("EMA Cross Down for ticker: %s", ticker)

            # if len(self.long_position) > 0:
            #     self.close_long_position()

            # self.open_short_position()

    def on_bid(self, ticker, tick):
        logger.debug10("Begin Function")
        logger.debug("Run On Bid")
        logger.debug("Ticker: %s", ticker)
        logger.debug("Tick: %s", tick)
        logger.debug10("End Function")

    def on_end(self):
        self.brokerclient.req_global_cancel()
        if len(self.long_position) > 0:
            self.close_long_position()
        if len(self.short_position) > 0:
            self.close_short_position()

    def on_high(self, ticker, tick):
        logger.debug10("Begin Function")
        logger.debug("Run On High")
        logger.debug("Ticker: %s", ticker)
        logger.debug("Tick: %s", tick)
        logger.debug10("End Function")

    def on_last(self, ticker, tick):
        logger.debug10("Begin Function")
        logger.debug("Run On Last")
        logger.debug("Ticker: %s", ticker)
        logger.debug("Tick: %s", tick)
        logger.debug10("End Function")

    def on_low(self, ticker, tick):
        logger.debug10("Begin Function")
        logger.debug("Run On Low")
        logger.debug("Ticker: %s", ticker)
        logger.debug("Tick: %s", tick)
        logger.debug10("End Function")

    def on_tick(self, ticker, tick):
        logger.debug10("Begin Function")
        logger.debug("Run On Tick")
        logger.debug("Ticker: %s", ticker)
        logger.debug("Tick: %s", tick)
        logger.debug10("End Function")


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
