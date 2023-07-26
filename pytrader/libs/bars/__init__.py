"""!
@package pytrader.libs.bars

Provides Bar Data

@author G. S. Derber
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


@file pytrader/libs/bars/__init__.py
"""
# Standard libraries
import datetime
import math
import os
import pathlib
import time

from statistics import mean

# 3rd Party libraries
import numpy
import pandas

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader import git_branch

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

        @param args:
        @param kwargs:

        @return None
        """
        ## Ticker for Bar
        self.ticker = args[0]

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
        class_name = type(self).__name__
        if self.bars is None:
            if len(self.bar_list) == 0:
                message = f"{class_name}({self.bar_size} bars for {self.ticker} is empty)"
            else:
                self.create_dataframe()
                message = f"{class_name}" \
                    f"{self.bar_size} for {self.ticker}:" \
                    f"{self.bars}"
        else:
            message = f"{class_name}" \
                f"{self.bar_size} for {self.ticker}:" \
                f"{self.bars}"

        return message

    def append_bar(self, bar: list):
        self.bar_list.append(bar)
        self._append_dataframe()

    def create_dataframe(self):
        logger.debug10("Begin Function")
        if self.bar_size in self.bar_size_long_duration:
            datetime_str = "Date"
            datetime_fmt = "%Y%m%d"
        else:
            datetime_str = "DateTime"
            datetime_fmt = "%Y%m%d %H:%M:%S %Z"

        logger.debug9("Bar List: %s", self.bar_list)

        self.bars = pandas.DataFrame(
            self.bar_list,
            columns=[datetime_str, "Open", "High", "Low", "Close", "Volume", "WAP", "Count"])
        self.bars[datetime_str] = pandas.to_datetime(self.bars[datetime_str], format=datetime_fmt)
        logger.debug10("End Function")

    def rescale(self, size):
        seconds = self._bar_seconds(size)
        bar_datetime = datetime.datetime.strptime(self.bar_list[-1][0], "%Y%m%d %H:%M:%S %Z")
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
            rtb_wap = mean(l[6] for l in bar_list)
            rtb_count = sum(l[7] for l in bar_list)

            new_bar = [
                rtb_date, rtb_open, rtb_high, rtb_low, rtb_close, rtb_volumn, rtb_wap, rtb_count
            ]

            return new_bar

        else:
            return None

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _append_dataframe(self):
        bar_list = [self.bar_list[-1]]

        logger.debug10("Begin Function")
        if self.bar_size in self.bar_size_long_duration:
            datetime_str = "Date"
            datetime_fmt = "%Y%m%d"
        else:
            datetime_str = "DateTime"
            datetime_fmt = "%Y%m%d %H:%M:%S %Z"

        logger.debug9("Bar List: %s", self.bar_list)

        bars_pd = pandas.DataFrame(
            bar_list,
            columns=[datetime_str, "Open", "High", "Low", "Close", "Volume", "WAP", "Count"])
        bars_pd[datetime_str] = pandas.to_datetime(bars_pd[datetime_str], format=datetime_fmt)

        self.bars = pandas.concat([self.bars, bars_pd], ignore_index=True)

        logger.debug10("End Function")

    def _bar_conversion(self, size):
        bar_conversion = {
            "5 secs": 1,
            "15 secs": 3,
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
            "15 secs": 15,
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
        self.long_period = {}
        self.long_period_count = {}
        self.medium_period = {}
        self.medium_period_count = {}
        self.short_period = {}
        self.short_period_count = {}
        self.print_columns = ["DateTime", "Open", "High", "Low", "Close", "Volume", "WAP", "Count"]
        super().__init__(*args, **kwargs)

    def __repr__(self):
        class_name = type(self).__name__
        if self.bars is None:
            if len(self.bar_list) == 0:
                message = f"{class_name}({self.bar_size} bars for {self.ticker} is empty)"
            else:
                self.create_dataframe()
                message = f"{class_name}\n" \
                    f"{self.bar_size} bars for {self.ticker}:\n" \
                    f"{self.bars}"
        else:
            if "EMA" in self.long_period_count.keys():
                message = f"{class_name}\n" \
                    f"{self.bar_size} for bars {self.ticker}:\n" \
                    f"{self.bars[self.print_columns].tail(self.long_period_count['EMA'])}"
            else:
                message = f"{class_name}\n" \
                    f"{self.bar_size} for bars {self.ticker}:\n" \
                    f"{self.bars[self.print_columns].tail(10)}"
        return message

    def calculate_adx(self, span: int = 14, print_column: bool = True):
        atr_col_name = str(span) + "ATR"
        moving_average = "smma"
        alpha = 1.0 / span

        #if atr_col_name not in self.bars.columns:
        self.calculate_atr(span, moving_average, alpha, False, False)

        self.bars["H-pH"] = self.bars["High"] - self.bars["High"].shift(1)
        self.bars["pL-L"] = self.bars["Low"].shift(1) - self.bars["Low"]
        self.bars["+DX"] = numpy.where(
            (self.bars["H-pH"] > self.bars["pL-L"]) & (self.bars["H-pH"] > 0), self.bars["H-pH"],
            0.0)
        self.bars["-DX"] = numpy.where(
            (self.bars["pL-L"] > self.bars["H-pH"]) & (self.bars["pL-L"] > 0), self.bars["pL-L"],
            0.0)

        self.bars["S+DM"] = self.bars["+DX"].ewm(alpha=alpha, adjust=False).mean()
        self.bars["S-DM"] = self.bars["-DX"].ewm(alpha=alpha, adjust=False).mean()
        self.bars["+DMI"] = (self.bars["S+DM"] / self.bars[atr_col_name]) * 100
        self.bars["-DMI"] = (self.bars["S-DM"] / self.bars[atr_col_name]) * 100

        self.bars["DX"] = (numpy.abs(self.bars["+DMI"] - self.bars["-DMI"]) /
                           (self.bars["+DMI"] + self.bars["-DMI"])) * 100
        self.bars["ADX"] = self.bars["DX"].ewm(alpha=alpha, adjust=False).mean()

        # if "+DX" not in self.print_columns and print_column:
        #     self.print_columns.append("+DX")
        # if "-DX" not in self.print_columns and print_column:
        #     self.print_columns.append("-DX")
        # if "S+DM" not in self.print_columns and print_column:
        #     self.print_columns.append("S+DM")
        # if "S-DM" not in self.print_columns and print_column:
        #     self.print_columns.append("S-DM")
        if "+DMI" not in self.print_columns and print_column:
            self.print_columns.append("+DMI")
        if "-DMI" not in self.print_columns and print_column:
            self.print_columns.append("-DMI")
        if "DX" not in self.print_columns and print_column:
            self.print_columns.append("DX")
        if "ADX" not in self.print_columns and print_column:
            self.print_columns.append("ADX")

    def calculate_atr(self,
                      span: int = 14,
                      moving_average: str = "SMA",
                      alpha: float = 0.0,
                      print_column: bool = True):
        #if "TrueRange" not in self.bars.columns:
        self.calculate_true_range(span, print_column, False)

        col_name = str(span) + "ATR"

        if moving_average == "smma":
            self.bars[col_name] = self.bars["TrueRange"].ewm(alpha=alpha, adjust=False).mean()
        else:
            self.bars[col_name] = self.bars["TrueRange"].rolling(span).mean()

        if col_name not in self.print_columns and print_column:
            self.print_columns.append(col_name)

        return self.bars[col_name].iloc[-1]

    def calculate_atr_stddev(self, span: int = 14, print_column: bool = True):

        atr_col_name = str(span) + "ATR"

        col_name = str(span) + "ATRσ"
        #if atr_col_name not in self.bars.columns:
        self.calculate_atr(span, print_column)

        self.bars[col_name] = self.bars[atr_col_name].rolling(span).std(ddof=0)

        if col_name not in self.print_columns and print_column:
            self.print_columns.append("ATRσ")

    def calculate_bbands(self,
                         span: int = 20,
                         stddev: int = 2,
                         moving_average: str = "sma",
                         print_column: bool = True):
        self.bars["Typical_Price"] = (self.bars["High"] + self.bars["Low"] + self.bars["Close"]) / 3
        self.bars["BBands_σ"] = self.bars["Typical_Price"].rolling(span).std(ddof=0)

        if moving_average == "ema":
            self.bars["BBands_MA"] = self.bars["Typical_Price"].ewm(span=span, adjust=False).mean()
        else:
            self.bars["BBands_MA"] = self.bars["Typical_Price"].rolling(span).mean()

        bband_upper_name = "BBandU_" + str(stddev) + "σ"
        bband_lower_name = "BBandL_" + str(stddev) + "σ"
        self.bars[bband_upper_name] = self.bars["BBands_MA"] + stddev * self.bars["BBands_σ"]
        self.bars[bband_lower_name] = self.bars["BBands_MA"] - stddev * self.bars["BBands_σ"]

        if "BBands_MA" not in self.print_columns and print_column:
            self.print_columns.append("BBands_MA")
        if bband_upper_name not in self.print_columns and print_column:
            self.print_columns.append(bband_upper_name)
        if bband_lower_name not in self.print_columns and print_column:
            self.print_columns.append(bband_lower_name)

    def calculate_column_diff(self, column: str, print_column: bool = True):
        col_name = column + "Δ"
        self.bars[col_name] = self.bars[col_name].diff()

        if col_name not in self.print_columns and print_column:
            self.print_columns.append(col_name)

    def calculate_columns_ave(self, columns: list, print_column: bool = True):
        col_name = "("
        col_sum = 0
        col_len = len(columns)

        for column in columns:
            col_name = col_name + column
            col_sum = col_sum + self.bars[column]

        col_name = col_name + ") Ave"

        self.bars[col_name] = col_sum / col_len

        if col_name not in self.print_columns and print_column:
            self.print_columns.append(col_name)

    def calculate_columns_delta(self, column1, column2, print_column: bool = True):
        col_name = column1 + "-" + column2 + "Δ"
        self.bars[col_name] = self.bars[column1] - self.bars[column2]

        if col_name not in self.print_columns and print_column:
            self.print_columns.append(col_name)

    def calculate_cumsum(self, column: str):
        col_name = column + "_CumSum"
        self.bars[col_name] = self.bars[column].cumsum()

    def calculate_squared(self, column: str):
        col_name = column + "_Squared"
        self.bars[col_name] = self.bars[column] * self.bars[column]

    def calculate_donchain_channel(self, span: int = 20, print_column: bool = True):
        self.bars["DC_Upper"] = self.bars["High"].rolling(span).max()
        self.bars["DC_Lower"] = self.bars["Low"].rolling(span).min()
        self.bars["DC_Middle"] = (self.bars["DC_Upper"] + self.bars["DC_Lower"]) / 2

        if "DC_Upper" not in self.print_columns and print_column:
            self.print_columns.append("DC_Upper")
        if "DC_Middle" not in self.print_columns and print_column:
            self.print_columns.append("DC_Middle")
        if "DC_Lower" not in self.print_columns and print_column:
            self.print_columns.append("DC_Lower")

    def calculate_ema(self, span: int, span_type: str, print_column: bool = True):
        col_name = str(span) + "EMA"

        if span_type == "long":
            self.long_period["EMA"] = col_name
            self.long_period_count["EMA"] = span
        elif span_type == "medium":
            self.medium_period["EMA"] = col_name
            self.medium_period_count["EMA"] = span
        elif span_type == "short":
            self.short_period["EMA"] = col_name
            self.short_period_count["EMA"] = span
        else:
            logger.error("Invalid Span Type: %s", span_type)

        self.bars[col_name] = self.bars["Close"].ewm(span=span, adjust=False).mean()

        if col_name not in self.print_columns and print_column:
            self.print_columns.append(col_name)

    def calculate_ocd_atr_delta(self, span: int = 14, print_column: bool = True):
        col_name = "OCD/ATRΔ"
        atr_col_name = str(span) + "ATR"

        self.bars[col_name] = abs(self.bars["Open/CloseΔ"]) - self.bars[atr_col_name]

        if col_name not in self.print_columns and print_column:
            self.print_columns.append(col_name)

    def calculate_sma(self, span: int, span_type: str, print_column: bool = True):
        col_name = str(span) + "SMA"

        if span_type == "long":
            self.long_period["SMA"] = col_name
            self.long_period_count["SMA"] = span
        elif span_type == "medium":
            self.medium_period["SMA"] = col_name
            self.medium_period_count["SMA"] = span
        elif span_type == "short":
            self.short_period["SMA"] = col_name
            self.short_period_count["SMA"] = span
        else:
            logger.error("Invalid Span Type: %s", span_type)

        self.bars[col_name] = self.bars["Close"].rolling(span).mean()

        if col_name not in self.print_columns and print_column:
            self.print_columns.append(col_name)

    def calculate_stochastic_oscillator(self,
                                        span: int = 14,
                                        moving_average: str = "sma",
                                        print_column: bool = True):

        high_col_name = str(span) + "_max"
        low_col_name = str(span) + "_min"

        self.bars[high_col_name] = self.bars["High"].rolling(span).max()
        self.bars[low_col_name] = self.bars["Low"].rolling(span).min()
        self.bars["Fast Stochastic (%K)"] = (self.bars["Close"] - self.bars[low_col_name]) / (
            self.bars[high_col_name] - self.bars[low_col_name]) * 100
        if moving_average == "ema":
            self.bars["Slow Stochastic (%D)"] = self.bars["Fast Stochastic (%K)"].ewm(
                span=3, adjust=False).mean()
        else:
            self.bars["Slow Stochastic (%D)"] = self.bars["Fast Stochastic (%K)"].rolling(3).mean()

        if "Fast Stochastic (%K)" not in self.print_columns and print_column:
            self.print_columns.append("Fast Stochastic (%K)")
        if "Slow Stochastic (%D)" not in self.print_columns and print_column:
            self.print_columns.append("Slow Stochastic (%D)")

    def calculate_true_range(self, print_column: bool = True):
        self.bars["TR1"] = abs(self.bars["High"] - self.bars["Low"])
        self.bars["TR2"] = abs(self.bars["High"] - self.bars["Close"].shift())
        self.bars["TR3"] = abs(self.bars["Low"] - self.bars["Close"].shift())
        self.bars["TrueRange"] = self.bars[["TR1", "TR2", "TR3"]].max(axis=1)

        if "TrueRange" not in self.print_columns and print_column:
            self.print_columns.append("TrueRange")

    def gen_index(self):
        self.bars["Index"] = range(len(self.bars))

    def get_last_row(self, column: str = ""):
        if column:
            return self.bars[column].iloc[-1]
        else:
            return self.bars.tail(1).copy()

    def is_cross_up(self, moving_ave_name: str):
        previous_short = self.bars[self.short_period[moving_ave_name]].iloc[-2]
        previous_long = self.bars[self.long_period[moving_ave_name]].iloc[-2]

        current_short = self.bars[self.short_period[moving_ave_name]].iloc[-1]
        current_long = self.bars[self.long_period[moving_ave_name]].iloc[-1]

        return (current_short >= current_long) & (previous_short <= previous_long)

    def is_cross_down(self, moving_ave_name: str):
        previous_short = self.bars[self.short_period[moving_ave_name]].iloc[-2]
        previous_long = self.bars[self.long_period[moving_ave_name]].iloc[-2]

        current_short = self.bars[self.short_period[moving_ave_name]].iloc[-1]
        current_long = self.bars[self.long_period[moving_ave_name]].iloc[-1]

        return (current_short <= current_long) & (previous_short >= previous_long)

    def save_dataframe(self):
        home = os.path.expanduser("~") + "/"
        today_date = str(datetime.date.today())

        if git_branch == "main":
            directory = home + "Documents/investing/" + today_date + "/" + self.bar_size + "/"
        elif git_branch.startswith("release"):
            directory = home + "Documents/investing/release/" + today_date + "/" + self.bar_size + "/"
        else:
            directory = home + "Documents/investing/development/" + today_date + "/" + self.bar_size + "/"

        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
        filename = directory + self.ticker + ".csv"
        logger.debug("Saving dataframe to '%s'", filename)
        self.bars.to_csv(filename, encoding="utf-8")
