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
# Standard libraries
import datetime
import time

# 3rd Party libraries
import pandas

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
class BasicBars():
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

        ## Data Frame used to hold bar history.
        self.bars = None

        ## List to hold bar history in list format
        self.bar_list = []

        ## Size of the bars
        self.bar_size = "1 day"

        if kwargs.get("bar_list"):
            if isinstance(kwargs["bar_list"][0], list):
                self.bar_list = kwargs["bar_list"]
            else:
                self.bar_list.append(kwargs["bar_list"])

        if kwargs.get("bar_size"):
            if kwargs["bar_size"]:
                self.bar_size = kwargs["bar_size"]

        ## List of Long Duration Bar Sizes
        self.bar_size_long_duration = ["1 day", "1 week", "1 month"]

        logger.debug10("End Function")

    def __repr__(self):
        if self.bars is None:
            if len(self.bar_list) == 0:
                return f'Bar(Size: "{self.bar_size}", Empty)'
            else:
                self.create_dataframe()

            return f'Bar(Size: "{self.bar_size}", "Bars: "{self.bars})'

    def append_bar(self, bar: list):
        # FIXME: If length < list_length, the following changes should be made:
        #
        # Open = last row self.bar_list open
        # High = max rdb_high, last row self.bar_list high
        # Low = min rdb_low, last row self.bar_list low
        #
        # Finally, the last row should be modified, rather than a new row appended

        self.bar_list.append(bar)

    def create_dataframe(self):
        logger.debug10("Begin Function")
        if self.bar_size in self.bar_size_long_duration:
            datetime_str = "Date"
            datetime_fmt = "%Y%m%d"
        else:
            datetime_str = "DateTime"
            datetime_fmt = "%Y%m%d %H:%M:%S %Z"

        logger.debug3("Bar List: %s", self.bar_list)

        self.bars = pandas.DataFrame(self.bar_list,
                                     columns=[
                                         datetime_str, "Open", "High", "Low",
                                         "Close", "Volume", "Count"
                                     ])
        self.bars[datetime_str] = pandas.to_datetime(self.bars[datetime_str],
                                                     format=datetime_fmt)
        logger.debug10("End Function")

    def rescale(self, size):
        seconds = self._bar_seconds(size)
        bar_datetime = datetime.datetime.strptime(self.bar_list[-1][0],
                                                  "%Y%m%d %H:%M:%S %Z")
        unixtime = int(time.mktime(bar_datetime.timetuple()))

        # We use '55' here because we are converting 5 second bars, and the timestamp is from the
        # open of the bar (Open = 11:09:55 Close = 11:10:00)

        unixtime += 5
        if unixtime % seconds == 0:
            list_length = self._bar_conversion(size)
            length = min(len(self.bar_list), list_length)

            bar_list = self.bar_list[-length:]
            rtb_date = bar_list[0][0]
            rtb_open = bar_list[0][1]
            rtb_high = max(l[2] for l in bar_list)
            rtb_low = min(l[3] for l in bar_list)
            rtb_close = bar_list[-1][4]
            rtb_volumn = sum(l[5] for l in bar_list)
            rtb_count = sum(l[6] for l in bar_list)

            new_bar = [
                rtb_date, rtb_open, rtb_high, rtb_low, rtb_close, rtb_volumn,
                rtb_count
            ]

            return new_bar

        else:
            return None

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _bar_conversion(self, size):
        bar_conversion = {
            "5 secs": 1,
            "30 secs": 6,
            "1 min": 12,
            "5 mins": 60,
            "15 mins": 180,
            "30 mins": 360,
            "1 hour": 720
        }
        return bar_conversion[size]

    def _bar_seconds(self, size):
        bar_seconds = {
            "rtb": 5,
            "5 secs": 5,
            "30 secs": 30,
            "1 min": 60,
            "5 mins": 300,
            "15 mins": 900,
            "30 mins": 1800,
            "1 hour": 3600
        }

        return bar_seconds[size]


class Bars(BasicBars):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calculate_ema(self, span, span_type):
        name = str(span) + "EMA"

        if span_type == "long":
            self.long_period = name
        elif span_type == "short":
            self.short_period = name
        else:
            logger.error("Invalid Span Type: %s", span_type)
        self.bars[name] = self.bars["Close"].ewm(span=span,
                                                 adjust=False).mean()

    def get_last_close(self):
        return self.bars["Close"].iloc[-1]

    def print_bar(self, ticker):
        logger.debug2("DataFrame for %s:\n%s", ticker, self.bars.tail(10))

    def calculate_sma(self, span):
        name = str(span) + "SMA"
        self.bars[name] = self.bars["Close"].rolling(span).mean()

    def is_cross_up(self):
        previous_short = self.bars[self.short_period].iloc[-2]
        previous_long = self.bars[self.long_period].iloc[-2]

        current_short = self.bars[self.short_period].iloc[-1]
        current_long = self.bars[self.long_period].iloc[-1]

        return ((current_short >= current_long) &
                (previous_short <= previous_long))

    def is_cross_down(self):
        previous_short = self.bars[self.short_period].iloc[-2]
        previous_long = self.bars[self.long_period].iloc[-2]

        current_short = self.bars[self.short_period].iloc[-1]
        current_long = self.bars[self.long_period].iloc[-1]

        return ((current_short <= current_long) &
                (previous_short >= previous_long))
