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
#import queue
import sys

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
        self.bars = pandas.DataFrame()

        ## List to hold bar history in list format
        self.bar_list = []

        ## Size of the bars
        self.bar_size = "1 day"

        if kwargs.get("bar_size"):
            if kwargs["bar_size"]:
                self.bar_size = kwargs["bar_size"]

        logger.debug10("End Function")

    def append_bar(self, bar: list):
        self.bar_list.append(bar)

    def get_bars(self):
        return self.bars

    def convert_bars_to_panda(self):
        logger.debug10("Begin Function")
        if self.bar_size in self.bar_size_long_duration:
            datetime_str = "Date"
            datetime_fmt = "%Y%m%d"
        else:
            datetime_str = "DateTime"
            datetime_fmt = "%Y%m%d %H:%M:%S %Z"

        self.bars = pandas.DataFrame(self.bar_list,
                                     columns=[
                                         datetime_str, "Open", "High", "Low",
                                         "Close", "Volume", "Count"
                                     ])
        self.bars[datetime_str] = pandas.to_datetime(self.bars[datetime_str],
                                                     format=datetime_fmt)

        logger.debug10("End Function")


class Bars(BasicBars):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    def calculate_ema(self, span):
        name = str(span) + "EMA"
        self.bars[name] = self.bars["Close"].ewm(span=span,
                                                 adjust=False).mean()

    def calculate_sma(self, span):
        name = str(span) + "SMA"
        self.bars[name] = self.bars["Close"].rolling(span).mean()
