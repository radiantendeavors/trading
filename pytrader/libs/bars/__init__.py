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
        self.ohlc_bars = None

        ## List to hold bar history in list format
        self.ohlc_bar_list = []

        ## Size of the bars
        self.ohlc_bar_size = "1 day"

        if kwargs.get("bar_list"):
            if isinstance(kwargs["bar_list"][0], list):
                self.ohlc_bar_list = kwargs["bar_list"]
            else:
                self.ohlc_bar_list.append(kwargs["bar_list"])

        if kwargs.get("bar_size"):
            if kwargs["bar_size"]:
                self.ohlc_bar_size = kwargs["bar_size"]

        ## List of Long Duration Bar Sizes
        self.bar_size_long_duration = ["1 day", "1 week", "1 month"]

        logger.debug10("End Function")

    def __repr__(self):
        class_name = type(self).__name__
        if self.ohlc_bars is None:
            if len(self.ohlc_bar_list) == 0:
                message = f"{class_name}({self.ohlc_bar_size} bars for {self.ticker} is empty)"
            else:
                self.create_dataframe()
                message = f"{class_name}" \
                    f"{self.ohlc_bar_size} for {self.ticker}:" \
                    f"{self.ohlc_bars}"
        else:
            message = f"{class_name}" \
                f"{self.ohlc_bar_size} for {self.ticker}:" \
                f"{self.ohlc_bars}"

        return message

    def append_bar(self, ohlc_bar: list) -> None:
        """!
        Appends new bar data to existing bar list.

        @param ohlc_bar: List containing new bar data.

        @return None
        """
        if not isinstance(ohlc_bar[0], list):
            self.ohlc_bar_list.append(ohlc_bar)
            self._append_dataframe()

    def create_dataframe(self) -> None:
        """!
        Creates a dataframe from the list of bars.

        @return None
        """
        self.ohlc_bars = self._create_dataframe(self.ohlc_bar_list)

    def rescale(self, size: str):
        """!
        Rescales a smaller bar size to a larger bar size.

        @param size: The requested larger bar size.

        @return list
        @return None
        """
        seconds = self._bar_seconds(size)
        bar_datetime = datetime.datetime.strptime(self.ohlc_bar_list[-1][0], "%Y%m%d %H:%M:%S %Z")
        unixtime = int(time.mktime(bar_datetime.timetuple()))

        # We use '55' here because we are converting 5 second bars, and the timestamp is from the
        # open of the bar (Open = 11:09:55 Close = 11:10:00)
        unixtime += 5
        if unixtime % seconds == 0:
            list_length = self._bar_conversion(size)
            length = min(len(self.ohlc_bar_list), list_length)

            bar_list = self.ohlc_bar_list[-length:]
            rtb_date = bar_list[0][0]
            rtb_open = bar_list[0][1]
            rtb_high = max(l[2] for l in bar_list)
            rtb_low = min(l[3] for l in bar_list)
            rtb_close = bar_list[-1][4]
            rtb_volumn = sum(l[5] for l in bar_list)
            rtb_wap = mean(l[6] for l in bar_list)
            rtb_count = sum(l[7] for l in bar_list)

            return [
                rtb_date, rtb_open, rtb_high, rtb_low, rtb_close, rtb_volumn, rtb_wap, rtb_count
            ]

        return None

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _append_dataframe(self):
        bar_list = [self.ohlc_bar_list[-1]]
        bars_df = self._create_dataframe(bar_list)
        self.ohlc_bars = pandas.concat([self.ohlc_bars, bars_df], ignore_index=True)

    def _bar_conversion(self, size):
        bar_conversion = {
            "5 secs": 1,
            "15 secs": 3,
            "30 secs": 6,
            "1 min": 12,
            "5 mins": 60,
            "15 mins": 180,
            "30 mins": 360,
            "1 hour": 720,
            "1 day": 17280
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
            "1 hour": 3600,
            "1 day": 86400
        }

        return bar_seconds[size]

    def _create_dataframe(self, bar_list: list) -> pandas.DataFrame:
        """!
        Creates a dataframe from the list of bars.

        @param bar_list: List of bars to use for the dataframe.

        @return None
        """
        if self.ohlc_bar_size in self.bar_size_long_duration:
            datetime_str = "Date"
            datetime_fmt = "%Y%m%d"
        else:
            datetime_str = "DateTime"
            datetime_fmt = "%Y%m%d %H:%M:%S %Z"

        try:
            bars_df = pandas.DataFrame(
                bar_list,
                columns=[datetime_str, "Open", "High", "Low", "Close", "Volume", "WAP", "Count"])
            bars_df[datetime_str] = pandas.to_datetime(bars_df[datetime_str], format=datetime_fmt)
            return bars_df

        except (AssertionError, ValueError) as msg:
            logger.critical("Failed to Create DataFrame for %s: %s", self.ticker,
                            self.ohlc_bar_size)
            if self.ohlc_bars is not None:
                logger.critical("Existing DataFrame: %s", self.ohlc_bars)
            logger.critical("Message: %s", msg)
            logger.critical("Bar List: %s", bar_list)
            return None


class Bars(BasicBars):
    """!
    Bar Class manages bar requirements used by strategies.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.long_period = {}
        self.long_period_count = {}
        self.medium_period = {}
        self.medium_period_count = {}
        self.short_period = {}
        self.short_period_count = {}

        if self.ohlc_bar_size in self.bar_size_long_duration:
            dt_col = "Date"
        else:
            dt_col = "DateTime"

        self.print_columns = [dt_col, "Open", "High", "Low", "Close", "Volume", "WAP", "Count"]

    def __repr__(self):
        class_name = type(self).__name__
        if self.ohlc_bars is None:
            if len(self.ohlc_bar_list) == 0:
                message = f"{class_name}({self.ohlc_bar_size} bars for {self.ticker} is empty)"
            else:
                self.create_dataframe()
                message = f"{class_name}\n" \
                    f"{self.ohlc_bar_size} bars for {self.ticker}:\n" \
                    f"{self.ohlc_bars}"
        else:
            num_rows = 10
            if "EMA" in list(self.long_period_count):
                num_rows = self.long_period_count["EMA"]

            message = f"{class_name}\n" \
                f"{self.ohlc_bar_size} for bars {self.ticker}:\n" \
                f"{self.ohlc_bars[self.print_columns].round(3).tail(num_rows)}"

        return message

    def calculate_adx(self,
                      span: int = 14,
                      moving_average: str = "smma",
                      print_column: bool = True):
        """!
        Average Directional Index

        https://www.investopedia.com/terms/a/adx.asp

        NOTE: Matches Trader Workstation, when moving_average = "ema"
        """
        self.calculate_dmi(span, moving_average, False)

        self.ohlc_bars["DX"] = (numpy.abs(self.ohlc_bars["+DMI"] - self.ohlc_bars["-DMI"]) /
                                numpy.abs(self.ohlc_bars["+DMI"] + self.ohlc_bars["-DMI"])) * 100

        if moving_average.lower() == "sma":
            self.ohlc_bars["ADX"] = self.ohlc_bars["DX"].rolling(span=span).mean()
        elif moving_average.lower() == "ema":
            self.ohlc_bars["ADX"] = self.ohlc_bars["DX"].ewm(span=span, adjust=False).mean()
        else:
            alpha = 1.0 / span
            self.ohlc_bars["ADX"] = self.ohlc_bars["DX"].ewm(alpha=alpha, adjust=False).mean()

        if "DX" not in self.print_columns and print_column:
            self.print_columns.append("DX")
        if "ADX" not in self.print_columns and print_column:
            self.print_columns.append("ADX")

    def calculate_atr(self,
                      span: int = 14,
                      moving_average: str = "sma",
                      alpha: float = 0.0,
                      print_column: bool = True) -> None:
        """!
        Average True Range

        NOTE: Matches Trader Workstation when moving_average = "sma"

        @param span:
        @param moving_average:
        @param alpha:
        @param print_column:

        @return None
        """
        #if "TrueRange" not in self.bars.columns:
        self.calculate_true_range(print_column)

        col_name = str(span) + "ATR"

        if moving_average.lower() == "smma":
            col_name = str(span) + "ATR(" + moving_average + ")"
            self.ohlc_bars[col_name] = self.ohlc_bars["TrueRange"].ewm(alpha=alpha,
                                                                       adjust=False).mean()
        elif moving_average.lower() == "ema":
            self.ohlc_bars[col_name] = self.ohlc_bars["TrueRange"].ewm(span=span,
                                                                       adjust=False).mean()
        else:
            self.ohlc_bars[col_name] = self.ohlc_bars["TrueRange"].rolling(span).mean()

        if col_name not in self.print_columns and print_column:
            self.print_columns.append(col_name)

        return self.ohlc_bars[col_name].iloc[-1]

    def calculate_bbands(self,
                         span: int = 20,
                         stddev: int = 2,
                         moving_average: str = "sma",
                         typical_price: str = "",
                         print_column: bool = True):
        """
        Bollinger Bands

        https://www.investopedia.com/terms/b/bollingerbands.asp

        FIXME: This does not match Trader Workstation.  It seems to be very close when using "Close"
        for the typical price.
        """
        if typical_price:
            typical_price_col = typical_price
        else:
            typical_price_col = "Ave(HighLowClose)"
            self.calculate_columns_ave(["High", "Low", "Close"], False)

        self.ohlc_bars["BBandsσ"] = self.ohlc_bars[typical_price_col].rolling(span).std(ddof=0)

        if moving_average == "ema":
            self.ohlc_bars["BBands_MA"] = self.ohlc_bars[typical_price_col].ewm(
                span=span, adjust=False).mean()
        else:
            self.ohlc_bars["BBands_MA"] = self.ohlc_bars[typical_price_col].rolling(span).mean()

        bband_upper_name = "BBandU_" + str(stddev) + "σ"
        bband_lower_name = "BBandL_" + str(stddev) + "σ"
        self.ohlc_bars[
            bband_upper_name] = self.ohlc_bars["BBands_MA"] + stddev * self.ohlc_bars["BBandsσ"]
        self.ohlc_bars[
            bband_lower_name] = self.ohlc_bars["BBands_MA"] - stddev * self.ohlc_bars["BBandsσ"]

        if "BBands_MA" not in self.print_columns and print_column:
            self.print_columns.append("BBands_MA")
        if bband_upper_name not in self.print_columns and print_column:
            self.print_columns.append(bband_upper_name)
        if bband_lower_name not in self.print_columns and print_column:
            self.print_columns.append(bband_lower_name)

    def calculate_column_diff(self, column: str, print_column: bool = True) -> None:
        """!
        Calculates the diff between rows of a specified column.

        @param column: The column the diff calculation will be performed on.
        @param print_column: Boolean: True will add the column to the logged output, false will not.

        @return None
        """
        col_name = column + "Δ"
        self.ohlc_bars[col_name] = self.ohlc_bars[column].diff()

        if col_name not in self.print_columns and print_column:
            self.print_columns.append(col_name)

    def calculate_column_stddev(self, column: str, span: int, print_column: bool = True) -> None:
        """!
        Calculates the standard deviation of a column.

        @param column:
        @param span:
        @param print_column:

        @return None
        """
        col_name = column + "σ"
        self.ohlc_bars[col_name] = self.ohlc_bars[column].rolling(span).std(ddof=0)

        if col_name not in self.print_columns and print_column:
            self.print_columns.append(col_name)

    def calculate_columns_ave(self, columns: list, print_column: bool = True) -> None:
        """!
        Calculate the average of multiple columns.

        @param columns:
        @param print_column:

        @return None
        """
        col_name = "Ave("
        col_sum = 0
        col_len = len(columns)

        for column in columns:
            col_name = col_name + column
            col_sum = col_sum + self.ohlc_bars[column]

        col_name = col_name + ")"

        self.ohlc_bars[col_name] = col_sum / col_len

        if col_name not in self.print_columns and print_column:
            self.print_columns.append(col_name)

    def calculate_columns_delta(self,
                                column1: str,
                                column2: str,
                                print_column: bool = True) -> None:
        """!
        Calculates the difference between two columns.

        @param column1:
        @param column2:
        @param print_column:

        @return None
        """
        col_name = column1 + "-" + column2 + "Δ"
        self.ohlc_bars[col_name] = self.ohlc_bars[column1] - self.ohlc_bars[column2]

        if col_name not in self.print_columns and print_column:
            self.print_columns.append(col_name)

    def calculate_cumsum(self, column: str) -> None:
        """!
        Calculates the cumulative sum of a column.

        @param column:

        @return None
        """
        col_name = column + "_CumSum"
        self.ohlc_bars[col_name] = self.ohlc_bars[column].cumsum()

    def calculate_squared(self, column: str) -> None:
        """!
        Calculates the square of a column.

        @param column:

        @return None
        """
        logger.warning("Use calculate_exponent(column, exponent) instead.")
        self.calculate_exponent(column, 2)

    def calculate_exponent(self, column: str, exponent: float) -> None:
        """!
        Calculates the power of a column.

        @param column:
        @param exponent:

        @return None
        """
        col_name = column + "^" + exponent
        self.ohlc_bars[col_name] = pow(self.ohlc_bars[column], exponent)

    def calculate_dmi(self,
                      span: int = 20,
                      moving_average: str = "smma",
                      print_column: bool = True):
        """!
        Directional Movement Index

        https://www.investopedia.com/terms/d/dmi.asp

        NOTE: Matches Trader Workstation when moving_average = "ema"
        """

        atr_col_name = str(span) + "ATR(" + moving_average + ")"

        self.ohlc_bars["H-pH"] = self.ohlc_bars["High"] - self.ohlc_bars["High"].shift(1)
        self.ohlc_bars["pL-L"] = self.ohlc_bars["Low"].shift(1) - self.ohlc_bars["Low"]
        self.ohlc_bars["+DX"] = numpy.where(
            (self.ohlc_bars["H-pH"] > self.ohlc_bars["pL-L"]) & (self.ohlc_bars["H-pH"] > 0),
            self.ohlc_bars["H-pH"], 0.0)
        self.ohlc_bars["-DX"] = numpy.where(
            (self.ohlc_bars["pL-L"] > self.ohlc_bars["H-pH"]) & (self.ohlc_bars["pL-L"] > 0),
            self.ohlc_bars["pL-L"], 0.0)

        if moving_average.lower() == "ema":
            self.calculate_atr(span, moving_average, 0.0, False)
            self.ohlc_bars["S+DM"] = self.ohlc_bars["+DX"].ewm(span=span, adjust=False).mean()
            self.ohlc_bars["S-DM"] = self.ohlc_bars["-DX"].ewm(span=span, adjust=False).mean()
        elif moving_average.lower() == "sma":
            self.calculate_atr(span, moving_average, 0.0, False)
            self.ohlc_bars["S+DM"] = self.ohlc_bars["+DX"].rolling(span=span).mean()
            self.ohlc_bars["S-DM"] = self.ohlc_bars["-DX"].rolling(span=span).mean()
        else:
            alpha = 1.0 / span
            self.calculate_atr(span, moving_average, alpha, False)
            self.ohlc_bars["S+DM"] = self.ohlc_bars["+DX"].ewm(alpha=alpha, adjust=False).mean()
            self.ohlc_bars["S-DM"] = self.ohlc_bars["-DX"].ewm(alpha=alpha, adjust=False).mean()

        self.ohlc_bars["+DMI"] = (self.ohlc_bars["S+DM"] / self.ohlc_bars[atr_col_name]) * 100
        self.ohlc_bars["-DMI"] = (self.ohlc_bars["S-DM"] / self.ohlc_bars[atr_col_name]) * 100

        if "+DMI" not in self.print_columns and print_column:
            self.print_columns.append("+DMI")
        if "-DMI" not in self.print_columns and print_column:
            self.print_columns.append("-DMI")

    def calculate_correlation_cycle(self,
                                    span: int = 20,
                                    input_period: int = 20,
                                    print_column: bool = True):
        """!
        Ehler's Correlation Cycle as a Trend Indicator.
        """
        self.ohlc_bars["CCY_Cosine"] = numpy.cos(360 * self.ohlc_bars.index / span)
        self.calculate_cumsum("Close")
        self.calculate_cumsum("CCY_Cosine")
        self.calculate_squared("Close")
        self.calculate_squared("CCY_Cosine")
        self.ohlc_bars[
            "CCY_Close_x_Cosine"] = self.ohlc_bars["Close"] * self.ohlc_bars["CCY_Cosine"]
        self.calculate_cumsum("Close_Squared")
        self.calculate_cumsum("CCY_Close_x_Cosine")
        self.calculate_cumsum("CCY_Cosine_Squared")

        length = len(self.ohlc_bars.index)

        self.ohlc_bars["CCY_Var1"] = (
            length * self.ohlc_bars["Close_Squared_CumSum"] -
            self.ohlc_bars["Close_CumSum"] * self.ohlc_bars["Close_CumSum"])
        self.ohlc_bars["CCY_Var2"] = (
            length * self.ohlc_bars["CCY_Cosine_Squared_CumSum"] -
            self.ohlc_bars["CCY_Cosine_CumSum"] * self.ohlc_bars["CCY_Cosine_CumSum"])
        self.ohlc_bars["CCY_Var3"] = (
            length * self.ohlc_bars["CCY_Close_x_Cosine_CumSum"] -
            self.ohlc_bars["Close_CumSum"] * self.ohlc_bars["CCY_Cosine_CumSum"])

        self.ohlc_bars["CCY_Sqrt"] = numpy.emath.sqrt(self.ohlc_bars["CCY_Var1"] *
                                                      self.ohlc_bars["CCY_Var2"])

        self.ohlc_bars["CCY"] = numpy.where(
            (self.ohlc_bars["CCY_Var1"] > 0) & (self.ohlc_bars["CCY_Var2"] > 0),
            self.ohlc_bars["CCY_Var3"] / self.ohlc_bars["CCY_Sqrt"], 0)

        if "CCY" not in self.print_columns and print_column:
            self.print_columns.append("CCY")

    def calculate_correlation_cycle_rate_of_change(self,
                                                   span: int = 20,
                                                   input_period: int = 20,
                                                   print_column: bool = True):
        """!
        Ehler's Correlation Cycle Rate of change as a Trend Indicator.
        """
        self.calculate_correlation_cycle(span, input_period)
        self.ohlc_bars["SineCorr"] = -numpy.sin(360 * self.ohlc_bars.index / span)
        self.calculate_cumsum("SineCorr")
        self.calculate_squared("SineCorr")
        self.ohlc_bars["CloseSineCorr"] = self.ohlc_bars["Close"] * self.ohlc_bars["SineCorr"]
        self.calculate_cumsum("CloseSineCorr")
        self.calculate_cumsum("SineCorr_Squared")

        length = len(self.ohlc_bars.index)

        self.ohlc_bars["CCYROC_Var1"] = (
            length * self.ohlc_bars["Close_Squared_CumSum"] -
            self.ohlc_bars["Close_CumSum"] * self.ohlc_bars["Close_CumSum"])
        self.ohlc_bars["CCYROC_Var2"] = (
            length * self.ohlc_bars["SineCorr_Squared_CumSum"] -
            self.ohlc_bars["SineCorr_CumSum"] * self.ohlc_bars["SineCorr_CumSum"])
        self.ohlc_bars["CCYROC_Var3"] = (
            length * self.ohlc_bars["CloseSineCorr_CumSum"] -
            self.ohlc_bars["Close_CumSum"] * self.ohlc_bars["SineCorr_CumSum"])

        self.ohlc_bars["CCYROC_Sqrt"] = numpy.emath.sqrt(self.ohlc_bars["CCYROC_Var1"] *
                                                         self.ohlc_bars["CCYROC_Var2"])

        self.ohlc_bars["CCYROC"] = numpy.where(
            (self.ohlc_bars["CCYROC_Var1"] > 0) & (self.ohlc_bars["CCYROC_Var2"] > 0),
            self.ohlc_bars["CCYROC_Var3"] / self.ohlc_bars["CCYROC_Sqrt"], 0)

        if "CCYROC" not in self.print_columns and print_column:
            self.print_columns.append("CCYROC")

    def calculate_correlation_cycle_state(self,
                                          span: int = 40,
                                          input_period: int = 20,
                                          print_column: bool = True):
        """!
        Ehler's Correlation Cycle State as a Trend Indicator.
        """
        threshold = 360 / span
        col_name = "CCYState"
        #col_name = str(threshold) + "CCYState"
        self.calculate_correlation_cycle_rate_of_change(span / 2, input_period, print_column)

        self.ohlc_bars["CCY_Arctan"] = numpy.arctan2(self.ohlc_bars["CCY"],
                                                     self.ohlc_bars["CCYROC"])

        self.ohlc_bars["CCY_Angle1"] = numpy.where(
            self.ohlc_bars["CCYROC"] != 0, 90 + 180 / math.pi * self.ohlc_bars["CCY_Arctan"], 0)
        self.ohlc_bars["CCY_Angle2"] = numpy.where(self.ohlc_bars["CCYROC"] > 0,
                                                   self.ohlc_bars["CCY_Angle1"] - 180,
                                                   self.ohlc_bars["CCY_Angle1"])

        # FIXME: Something seems off with this function
        self.ohlc_bars["CCY_Angle3"] = numpy.where(
            ((self.ohlc_bars["CCY_Angle2"].shift() - self.ohlc_bars["CCY_Angle2"]) < 270) &
            (self.ohlc_bars["CCY_Angle2"] < self.ohlc_bars["CCY_Angle2"].shift()),
            self.ohlc_bars["CCY_Angle2"].shift(), self.ohlc_bars["CCY_Angle2"])

        self.ohlc_bars["CCY_Abs(AngleΔ)"] = abs(self.ohlc_bars["CCY_Angle3"] -
                                                self.ohlc_bars["CCY_Angle3"].shift())
        self.ohlc_bars[col_name] = numpy.where(self.ohlc_bars["CCY_Abs(AngleΔ)"] < threshold,
                                               numpy.where(self.ohlc_bars["CCY_Angle3"] < 0, -1, 1),
                                               0)

        if col_name not in self.print_columns and print_column:
            self.print_columns.append("CCYState")

    def calculate_donchain_channel(self, span: int = 20, print_column: bool = True):
        """!
        Donchain Channels

        https://www.investopedia.com/terms/d/donchianchannels.asp

        NOTE: This matches Trader Workstation
        """
        dc_upper_name = str(span) + "DC_Upper"
        dc_lower_name = str(span) + "DC_Lower"
        dc_middle_name = str(span) + "DC_Middle"

        self.ohlc_bars[dc_upper_name] = self.ohlc_bars["High"].rolling(span).max()
        self.ohlc_bars[dc_lower_name] = self.ohlc_bars["Low"].rolling(span).min()
        self.ohlc_bars[dc_middle_name] = (self.ohlc_bars[dc_upper_name] +
                                          self.ohlc_bars[dc_lower_name]) / 2

        if dc_upper_name not in self.print_columns and print_column:
            self.print_columns.append(dc_upper_name)
        if dc_middle_name not in self.print_columns and print_column:
            self.print_columns.append(dc_middle_name)
        if dc_lower_name not in self.print_columns and print_column:
            self.print_columns.append(dc_lower_name)

    def calculate_ema(self, span: int, span_type: str, print_column: bool = True):
        """!
        Exponentiial Moving Average

        https://www.investopedia.com/terms/e/ema.asp

        NOTE: This matches Trader Workstation
        """
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

        self.ohlc_bars[col_name] = self.ohlc_bars["Close"].ewm(span=span, adjust=False).mean()

        if col_name not in self.print_columns and print_column:
            self.print_columns.append(col_name)

    def calculate_kvo(self,
                      short_span: int = 34,
                      long_span: int = 55,
                      signal_span: int = 13,
                      moving_average: str = "ema",
                      signal_moving_average: str = "ema",
                      mode: str = "TradingView",
                      print_column: bool = True):
        """
        Klinger Volume Oscillator

        https://www.reddit.com/r/algotrading/comments/u275ue/help_with_klinger_volume_osilator/

        "Classic" Formula: https://www.investopedia.com/terms/k/klingeroscillator.asp

        FIXME: This does NOT match Trader Workstation
        """
        trend_col = "kTrend"

        self.ohlc_bars[
            "HLC"] = self.ohlc_bars["High"] + self.ohlc_bars["Low"] + self.ohlc_bars["Close"]

        if trend_col not in self.ohlc_bars.columns:
            self.ohlc_bars[trend_col] = 0

        self.ohlc_bars[trend_col] = numpy.where(
            self.ohlc_bars["HLC"].diff() == 0, 0,
            numpy.where(self.ohlc_bars["HLC"].diff() > 0, 1, -1))

        if mode == "TradingView":
            short_vf_ema_col = str(short_span) + "VF_EMA"
            long_vf_ema_col = str(long_span) + "VF_EMA"
            vf_col = "VolForce"
            kvo_col = "KVO"
            kvo_signal_col = "KVO_Signal"

            self.ohlc_bars[vf_col] = self.ohlc_bars["Volume"] * self.ohlc_bars[trend_col]
        else:
            short_vf_ema_col = str(short_span) + "VF_EMA(C)"
            long_vf_ema_col = str(long_span) + "VF_EMA(C)"
            cm_col_base = "klinger_cm_base"
            cm_col = "klinger_cm"
            vf_col = "VolForce(C)"
            kvo_col = "KVO(C)"
            kvo_signal_col = "KVO_Signal(C)"

            self.ohlc_bars["klinger_dm"] = self.ohlc_bars["High"] - self.ohlc_bars["Low"]

            if "klinger_cm" not in self.ohlc_bars.columns:
                self.ohlc_bars["klinger_cm"] = 0
            self.ohlc_bars[cm_col_base] = numpy.where(self.ohlc_bars[trend_col].diff() == 0,
                                                      self.ohlc_bars[cm_col].shift(1),
                                                      self.ohlc_bars["klinger_dm"].shift(1))
            self.ohlc_bars[cm_col] = numpy.where(
                self.ohlc_bars.index == 0, 0,
                self.ohlc_bars[cm_col_base] + self.ohlc_bars["klinger_dm"])
            self.ohlc_bars[vf_col] = self.ohlc_bars["Volume"] * numpy.abs(2 * (
                (self.ohlc_bars["klinger_dm"] / self.ohlc_bars[cm_col]) -
                1)) * self.ohlc_bars[trend_col] * 100

        if moving_average.lower() == "smma":
            alpha = 1.0 / short_span
            self.ohlc_bars[short_vf_ema_col] = self.ohlc_bars[vf_col].ewm(alpha=alpha,
                                                                          adjust=False).mean()
            alpha = 1.0 / long_span
            self.ohlc_bars[long_vf_ema_col] = self.ohlc_bars[vf_col].ewm(alpha=alpha,
                                                                         adjust=False).mean()

        else:
            self.ohlc_bars[short_vf_ema_col] = self.ohlc_bars[vf_col].ewm(span=short_span,
                                                                          adjust=False).mean()
            self.ohlc_bars[long_vf_ema_col] = self.ohlc_bars[vf_col].ewm(span=long_span,
                                                                         adjust=False).mean()

        self.ohlc_bars[kvo_col] = self.ohlc_bars[short_vf_ema_col] - self.ohlc_bars[long_vf_ema_col]

        if signal_moving_average.lower() == "smma":
            alpha = 1.0 / signal_span
            self.ohlc_bars[kvo_signal_col] = self.ohlc_bars[kvo_col].ewm(alpha=alpha,
                                                                         adjust=False).mean()
        elif signal_moving_average.lower() == "sma":
            self.ohlc_bars[kvo_signal_col] = self.ohlc_bars[kvo_col].rolling(signal_span).mean()
        else:
            self.ohlc_bars[kvo_signal_col] = self.ohlc_bars[kvo_col].ewm(span=signal_span,
                                                                         adjust=False).mean()

        if kvo_col not in self.print_columns and print_column:
            self.print_columns.append(kvo_col)
        if kvo_signal_col not in self.print_columns and print_column:
            self.print_columns.append(kvo_signal_col)

    def calculate_sma(self, span: int, span_type: str, print_column: bool = True):
        """Simple Moving Average

        https://www.investopedia.com/terms/s/sma.asp

        NOTE: This matches Trader Workstation
        """
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

        self.ohlc_bars[col_name] = self.ohlc_bars["Close"].rolling(span).mean()

        if col_name not in self.print_columns and print_column:
            self.print_columns.append(col_name)

    def calculate_stochastic_oscillator(self,
                                        span: int = 14,
                                        moving_average: str = "sma",
                                        print_column: bool = True):
        """
        Stochastic Oscillator

        https://www.investopedia.com/terms/s/stochasticoscillator.asp

        NOTE: Matches Trader Workstation when moving_average = "ema"
        """

        self.calculate_donchain_channel(span, False)

        high_col_name = str(span) + "DC_Upper"
        low_col_name = str(span) + "DC_Lower"
        fast_col_name = "FStochOsc(%K)"
        slow_col_name = "SStochOsc(%D)"

        self.ohlc_bars[fast_col_name] = (self.ohlc_bars["Close"] - self.ohlc_bars[low_col_name]) / (
            self.ohlc_bars[high_col_name] - self.ohlc_bars[low_col_name]) * 100
        if moving_average == "ema":
            self.ohlc_bars[slow_col_name] = self.ohlc_bars[fast_col_name].ewm(span=3,
                                                                              adjust=False).mean()
        else:
            self.ohlc_bars[slow_col_name] = self.ohlc_bars[fast_col_name].rolling(3).mean()

        if fast_col_name not in self.print_columns and print_column:
            self.print_columns.append(fast_col_name)
        if slow_col_name not in self.print_columns and print_column:
            self.print_columns.append(slow_col_name)

    def calculate_true_range(self, print_column: bool = True):
        """!
        Calculates the true range of the bars.

        @param print_column:

        @return None
        """
        self.ohlc_bars["TR1"] = abs(self.ohlc_bars["High"] - self.ohlc_bars["Low"])
        self.ohlc_bars["TR2"] = abs(self.ohlc_bars["High"] - self.ohlc_bars["Close"].shift())
        self.ohlc_bars["TR3"] = abs(self.ohlc_bars["Low"] - self.ohlc_bars["Close"].shift())
        self.ohlc_bars["TrueRange"] = self.ohlc_bars[["TR1", "TR2", "TR3"]].max(axis=1)

        if "TrueRange" not in self.print_columns and print_column:
            self.print_columns.append("TrueRange")

    def get_last_row(self, column: str = ""):
        """!
        Gets the last row of a column or dataframe.

        @param column:

        @return column_value if column is specified.
        @return dataframe if column is not specified.
        """
        if column:
            return self.ohlc_bars[column].iloc[-1]

        return self.ohlc_bars.tail(1).copy()

    def is_cross_up(self, moving_ave_name: str):
        """!
        Identifies if there has been a cross of two columns.

        @param moving_ave_name:

        @return Bool: True if cross has happened, False if no crossover has happened.
        """
        previous_short = self.ohlc_bars[self.short_period[moving_ave_name]].iloc[-2]
        previous_long = self.ohlc_bars[self.long_period[moving_ave_name]].iloc[-2]

        current_short = self.ohlc_bars[self.short_period[moving_ave_name]].iloc[-1]
        current_long = self.ohlc_bars[self.long_period[moving_ave_name]].iloc[-1]

        return (current_short >= current_long) & (previous_short <= previous_long)

    def is_cross_down(self, moving_ave_name: str):
        """!
        Identifies if there has been a cross of two columns.

        @param moving_ave_name:

        @return Bool: True if cross has happened, False if no crossover has happened.
        """
        previous_short = self.ohlc_bars[self.short_period[moving_ave_name]].iloc[-2]
        previous_long = self.ohlc_bars[self.long_period[moving_ave_name]].iloc[-2]

        current_short = self.ohlc_bars[self.short_period[moving_ave_name]].iloc[-1]
        current_long = self.ohlc_bars[self.long_period[moving_ave_name]].iloc[-1]

        return (current_short <= current_long) & (previous_short >= previous_long)

    def save_dataframe(self) -> None:
        """!
        Saves the dataframe to a csv file

        @return None
        """
        home = os.path.expanduser("~") + "/"
        today_date = str(datetime.date.today())
        doc_dir = home + "Documents/investing/"

        if git_branch == "main":
            directory = doc_dir + today_date + "/" + self.ohlc_bar_size + "/"
        elif git_branch.startswith("release"):
            directory = doc_dir + "release/" + today_date + "/" + self.ohlc_bar_size + "/"
        else:
            directory = doc_dir + "development/" + today_date + "/" + self.ohlc_bar_size + "/"

        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
        filename = directory + self.ticker + ".csv"
        logger.debug("Saving dataframe to '%s'", filename)
        self.ohlc_bars.to_csv(filename, encoding="utf-8", index=False)
