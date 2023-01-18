"""!
@package pytrader.libs.bars

Provides Bar Data

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


@file pytrader/libs/bars/__init__.py
"""
# System libraries
import pandas
import sys

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Bars():
    """!
    Contains bar history for a security
    """

    def __init__(self, *args, **kwargs):
        """!
        Initializes the class

        @param args -
        @param kwargs -

        @return None
        """

        ## Broker Client
        self.brokerclient = None

        ## Process Queue
        self.process_queue = None

        ## Data Frame used to hold bar history.
        self.bars = pandas.DataFrame()

        ## List to hold bar history in list format
        self.bar_list = []

        ## Bar contract
        self.contract = kwargs["contract"]

        ## Size of the bars
        self.bar_size = "1 day"

        ## Bar history length
        self.duration = None

        logger.debug10("Begin Function")
        if kwargs.get("brokerclient"):
            self.brokerclient = kwargs["brokerclient"]

        if kwargs["queue"]:
            self.process_queue = kwargs["queue"]

        if kwargs.get("bar_size"):
            self.bar_size = kwargs["bar_size"]

        if kwargs.get("duration"):
            self.duration = kwargs["duration"]

        if kwargs.get("keep_up_to_date"):
            self.keep_up_to_date = kwargs["keep_up_to_date"]
        else:
            self.keep_up_to_date = False

        self.bar_size_long_duration = ["1 day", "1 week", "1 month"]
        logger.debug10("End Function")

        return None

    def get_bars(self):
        return self.bars

    def retreive_bar_history(self, keep_up_to_date=False):
        logger.debug10("Begin Function")
        if self.brokerclient:
            self._retreive_broker_bar_history(keep_up_to_date)
        else:
            raise NotImplementedError

        logger.debug10("End Function")
        return None

    def _convert_bars_to_panda(self):
        logger.debug10("Begin Function")
        if self.bar_size in self.bar_size_long_duration:
            self.bars = pandas.DataFrame(self.bar_list,
                                         columns=[
                                             "Date", "Open", "High", "Low",
                                             "Close", "Volume", "WAP", "Count"
                                         ])
            self.bars["Date"] = pandas.to_datetime(self.bars["Date"],
                                                   format="%Y%m%d")
        else:
            self.bars = pandas.DataFrame(self.bar_list,
                                         columns=[
                                             "DateTime", "Open", "High", "Low",
                                             "Close", "Volume", "WAP", "Count"
                                         ])
            self.bars["DateTime"] = pandas.to_datetime(
                self.bars["DateTime"], format="%Y%m%d %H:%M:%S %Z")
        logger.debug10("End Function")

    def _retreive_broker_bar_history(self):
        req_id = self.brokerclient.req_historical_data(
            self.contract,
            self.bar_size,
            duration_str=self.duration,
            keep_up_to_date=self.keep_up_to_date)
        bar_list = self.brokerclient.get_data(req_id)
        logger.debug4("Bar List: %s", bar_list)

        for bar in bar_list:
            logger.debug3("Bar: %s", bar)
            date = bar.date
            open = bar.open
            high = bar.high
            low = bar.low
            close = bar.close
            volume = bar.volume
            wap = bar.wap
            count = bar.barCount

            self.bar_list.append(
                [date, open, high, low, close, volume, wap, count])

        logger.debug4("Bar List: %s", self.bar_list[0])
        self._convert_bars_to_panda()
        logger.debug10("End Function")

    def _set_duration(self):
        if not self.duration:
            if self.bar_size == "1 month":
                self.duration = "2 Y"
            elif self.bar_size == "1 week":
                self.duration = "1 Y"
            elif self.bar_size == "1 day":
                self.duration = "1 Y"
            elif self.bar_size == "1 hour":
                self.duration = "7 W"
            elif self.bar_size == "30 mins":
                self.duration = "4 W"
            elif self.bar_size == "15 mins":
                self.duration = "10 D"
            elif self.bar_size == "5 mins":
                self.duration = "4 D"
        return None

    def calculate_ema(self, span):
        name = str(span) + "EMA"
        self.bars[name] = self.bars["Close"].ewm(span=span,
                                                 adjust=False).mean()

    def calculate_sma(self, span):
        name = str(span) + "SMA"
        self.bars[name] = self.bars["Close"].rolling(span).mean()
