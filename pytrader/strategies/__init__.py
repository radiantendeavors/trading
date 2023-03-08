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

# 3rd Party libraries
import pandas
from ibapi import contract
from ibapi import order

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
#from pytrader.libs.securities import security

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

    def __init__(self, brokerclient):
        self.brokerclient = brokerclient

        self.endtime = datetime.datetime.combine(
            datetime.date.today(), datetime.time(hour=16, minute=16))
        self.time_now = datetime.datetime.now()
        self.real_time_bars = pandas.DataFrame(columns=[
            "DateTime", "Open", "High", "Low", "Close", "Volume", "Count"
        ])
        ## Position Status: -1 = short, 0 = Empty, 1 = long
        self.position_status = 0

    def run(self):
        logger.debug10("Begin Function")

        self.contract = contract.Contract()
        self.contract.symbol = self.security
        self.contract.secType = "STK"
        self.contract.exchange = "SMART"
        self.contract.currency = "USD"

        req_id = self.brokerclient.req_historical_data(self.contract,
                                                       self.bar_sizes,
                                                       duration_str="1 D")

        bar_list = self.brokerclient.get_data(req_id)

        adj_bar_list = []

        for bar in bar_list:
            logger.debug3("Bar: %s", bar)
            bar_date = bar.date
            bar_open = bar.open
            bar_high = bar.high
            bar_low = bar.low
            bar_close = bar.close
            bar_volume = bar.volume
            bar_wap = bar.wap
            bar_count = bar.barCount

            adj_bar_list.append([
                bar_date, bar_open, bar_high, bar_low, bar_close, bar_volume,
                bar_wap, bar_count
            ])

        self.bars = pandas.DataFrame(adj_bar_list,
                                     columns=[
                                         "DateTime", "Open", "High", "Low",
                                         "Close", "Volume", "WAP", "Count"
                                     ])
        self.bars["DateTime"] = pandas.to_datetime(self.bars["DateTime"],
                                                   format="%Y%m%d %H:%M:%S %Z")

        short_name = str(self.short_period) + "EMA"
        self.bars[short_name] = self.bars["Close"].ewm(span=self.short_period,
                                                       adjust=False).mean()

        long_name = str(self.long_period) + "EMA"
        self.bars[long_name] = self.bars["Close"].ewm(span=self.long_period,
                                                      adjust=False).mean()

        req_id = self.brokerclient.req_real_time_bars(self.contract)

        while self.time_now < self.endtime:
            real_time_bar = self.brokerclient.realtime_bar_queue[req_id].get()
            logger.debug("Real Time Bar: %s", real_time_bar)

            bar_datetime = datetime.datetime.fromtimestamp(
                real_time_bar[0]).strftime('%Y%m%d %H:%M:%S')
            bar_datetime_str = str(bar_datetime) + " EST"
            logger.debug("Bar DateTime: %s", bar_datetime)

            real_time_bar[0] = bar_datetime_str
            real_time_bar[5] = int(real_time_bar[5])
            real_time_bar[6] = float(real_time_bar[6])
            real_time_bar.append(0)
            real_time_bar.append(0)

            logger.debug("Bars: %s", self.bars.tail(5))
            logger.debug("Real Time Bar: %s", real_time_bar)

            # FIXME: Should check that the bar is not already in the dataframe
            # (only a problem when first starting)
            self.bars.loc[len(self.bars)] = real_time_bar

            short_name = str(self.short_period) + "EMA"
            self.bars[short_name] = self.bars["Close"].ewm(
                span=self.short_period, adjust=False).mean()

            long_name = str(self.long_period) + "EMA"
            self.bars[long_name] = self.bars["Close"].ewm(
                span=self.long_period, adjust=False).mean()

            logger.debug("Real Time Bar (with EMA): %s", self.bars.tail(20))

            previous_short = self.bars[short_name].iloc[-2]
            previous_long = self.bars[long_name].iloc[-2]

            current_short = self.bars[short_name].iloc[-1]
            current_long = self.bars[long_name].iloc[-1]

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

        logger.debug10("End Function")


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
