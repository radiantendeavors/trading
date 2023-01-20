"""!@package pytrader.strategies

Provides the Base Class for a Strategy.

@author Geoff S. derber
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

@file strategies/__init__.py

    Contains global variables for the pyTrader program.

"""
# System libraries
import datetime
import time

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs.securities import security

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
class Strategy():

    def __init__(self, brokerclient, queue, securities_list=[], bar_sizes=[]):
        self.brokerclient = brokerclient
        self.process_queue = queue
        self.securities = securities_list

        logger.debug("Bar Sizes: %s", bar_sizes)
        if bar_sizes:
            self.bar_size_list = bar_sizes
        else:
            self.bar_size_list = [
                "5 mins", "15 mins", "30 mins", "1 hour", "1 day"
            ]

        logger.debug("Bar Size List: %s", self.bar_size_list)

        self.intraday_bar_sizes = brokerclient.intraday_bar_sizes
        self.bar_size_long_duration = ["1 day", "1 week", "1 month"]
        self.investments = {}

        self.endtime = datetime.datetime.combine(
            datetime.date.today(), datetime.time(hour=20, minute=16))
        self.time_now = datetime.datetime.now()

    def set_investments(self):
        for item in self.securities:
            self.investments[item] = security.Security(
                security_type="etfs",
                ticker_symbol=item,
                brokerclient=self.brokerclient,
                process_queue=self.process_queue,
                bar_sizes=self.bar_size_list)
            self.investments[item].set_contract()

    def run_loop(self):
        prev_minute = self.time_now.minute - (self.time_now.minute % 5)
        time_rounded = self.time_now.replace(minute=prev_minute, second=0)

        for item in self.investments:
            self.investments[item].retrieve_bar_history(keep_up_to_date=True)

        for item in self.investments:
            self.investments[item].update_bars()

        while self.time_now < self.endtime:
            time_rounded += datetime.timedelta(minutes=5)

            time_now = datetime.datetime.now()
            time_to_wait = (time_rounded - time_now).total_seconds()

            logger.debug("Time To Wait: %s", time_to_wait)

            time.sleep(time_to_wait)

    def run_once(self):
        logger.debug("Begin Function")
        for item in self.securities:
            self.investments[item].retrieve_bar_history(keep_up_to_date=False)

            bars = self.investments[item].get_bars()
            logger.debug("Bars: %s", bars)
        logger.debug("End Function")
        return None

    def run(self):
        logger.debug10("Begin Function")
        self.set_investments()

        if set(self.bar_size_list).issubset(self.bar_size_long_duration):
            self.run_once()
        else:
            self.run_loop()
        logger.debug10("End Function")


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
