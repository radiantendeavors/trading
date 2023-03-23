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

from abc import ABCMeta, abstractmethod

# 3rd Party libraries
from ibapi import order

# System Library Overrides
from pytrader.libs.system import logging
from pytrader.libs.utilities import ipc

# Application Libraries

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

    __metaclass__ = ABCMeta

    def __init__(self):
        self.socket_client = ipc.IpcClient()

        self.time_now = datetime.datetime.now()
        self.bars = []

        self.long_position = []
        self.short_position = []

    @abstractmethod
    def continue_strategy(self):
        """!
        Checks various conditions for continuing to run the strategy.

        This function is Mandatory to define in each strategy.
        """
        # TODO: Experiment with Return False, and Raise if for if the strategy does not have this
        # defined.
        pass

    @abstractmethod
    def on_5sec_rtb(self, real_time_bar):
        pass

    @abstractmethod
    def on_bar(self):
        pass

    @abstractmethod
    def on_end(self):
        pass

    @abstractmethod
    def on_start(self):
        pass

    @abstractmethod
    def on_tick(self):
        pass

    def run(self):
        logger.debug10("Begin Function")

        try:
            self.socket_client.connect()
            self._send_tickers()

            logger.debug("Use Options: %s", self.use_options)
            if self.use_options:
                self._req_option_details()

            self._send_bar_sizes()
            self._req_bar_history()
            self._req_real_time_bars()
            #self._req_tick_by_tick_data()
            #self._req_market_data()

            while self.continue_strategy():
                data = self.socket_client.recv()
                self._process_data(data)
        finally:
            #self.on_end()
            self.socket_client.disconnect()

        # bar_adjustment = self._bar_conversion()

        # self.contract = contract.Contract()
        # self.contract.symbol = self.security
        # self.contract.secType = "STK"
        # self.contract.exchange = "SMART"
        # self.contract.currency = "USD"

        # req_id = self.brokerclient.req_historical_data(self.contract,
        #                                                self.bar_sizes,
        #                                                duration_str="1 D")

        # bar_list = self.brokerclient.get_data(req_id)

        # for bar in bar_list:
        #     logger.debug3("Bar: %s", bar)
        #     bar_date = bar.date
        #     bar_open = bar.open
        #     bar_high = bar.high
        #     bar_low = bar.low
        #     bar_close = bar.close
        #     bar_volume = bar.volume
        #     bar_count = bar.barCount

        #     self.bars.append([
        #         bar_date, bar_open, bar_high, bar_low, bar_close, bar_volume,
        #         bar_count
        #     ])

        # req_id = self.brokerclient.req_real_time_bars(self.contract)

        # real_time_bars = []

        # while self.time_now < self.endtime:
        #     real_time_bar = self.brokerclient.realtime_bar_queue[req_id].get()

        #     bar_datetime = datetime.datetime.fromtimestamp(
        #         real_time_bar[0]).strftime('%Y%m%d %H:%M:%S')
        #     bar_datetime_str = str(bar_datetime) + " EST"

        #     real_time_bar[0] = bar_datetime_str
        #     real_time_bar[5] = int(real_time_bar[5])
        #     real_time_bar[6] = float(real_time_bar[6])

        #     logger.debug("Real Time Bar: %s", real_time_bar)

        #     real_time_bars.append(real_time_bar)

        #     logger.debug("Bar adjustment: %s", bar_adjustment)
        #     if len(real_time_bars) == bar_adjustment:
        #         rtb_date = real_time_bars[0][0]
        #         rtb_open = real_time_bars[0][1]
        #         rtb_high = max(l[2] for l in real_time_bars)
        #         rtb_low = min(l[3] for l in real_time_bars)
        #         rtb_close = real_time_bars[-1][4]
        #         rtb_volumn = sum(l[5] for l in real_time_bars)
        #         rtb_count = sum(l[6] for l in real_time_bars)

        #         new_bar = [
        #             rtb_date, rtb_open, rtb_high, rtb_low, rtb_close,
        #             rtb_volumn, rtb_count
        #         ]
        #         self.bars.append(new_bar)

        #         self.bars_df = pandas.DataFrame(self.bars,
        #                                         columns=[
        #                                             "DateTime", "Open", "High",
        #                                             "Low", "Close", "Volume",
        #                                             "Count"
        #                                         ])
        #         self.bars_df["DateTime"] = pandas.to_datetime(
        #             self.bars_df["DateTime"], format="%Y%m%d %H:%M:%S %Z")

        #         self.on_bar()
        #         real_time_bars = []
        #     else:
        #         # This feels like a crappy way to check if the real_time bar exists
        #         try:
        #             self.on_5sec_rtb(real_time_bar)
        #         except Exception as msg:
        #             logger.debug5("Exception: %s", msg)

        logger.debug10("End Function")

    def close_long_position(self):
        contract = self.long_position.pop(0)
        sell_order = order.Order()
        sell_order.action = "SELL"
        sell_order.totalQuantity = self.quantity
        sell_order.orderType = "MKT"
        self.brokerclient.place_order(contract, sell_order)

    def open_long_position(self):
        buy_order = order.Order()
        buy_order.action = "BUY"
        buy_order.totalQuantity = self.quantity
        buy_order.orderType = "MKT"
        self.brokerclient.place_order(self.next_option_contract, buy_order)
        self.long_position.append(self.next_option_contract)

    def open_short_position(self):
        sell_order = order.Order()
        sell_order.action = "SELL"
        sell_order.totalQuantity = self.quantity
        sell_order.orderType = "MKT"
        self.brokerclient.place_order(self.next_option_contract, sell_order)
        self.short_position.append(self.next_option_contract)

    def close_short_position(self):
        contract = self.short_position.pop(0)
        buy_order = order.Order()
        buy_order.action = "BUY"
        buy_order.totalQuantity = self.quantity
        buy_order.orderType = "MKT"
        self.brokerclient.place_order(contract, buy_order)

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _bar_conversion(self):
        bar_conversion = {
            "5 secs": 1,
            "30 secs": 6,
            "1 min": 12,
            "5 mins": 60,
            "15 mins": 180,
            "30 mins": 360,
            "1 hr": 720
        }
        return bar_conversion[self.bar_sizes]

    def _process_data(self, data):
        logger.debug("Processing Data: %s", data)
        logger.debug("Data Type: %s", type(data))
        # if data.get("real_time_bars"):
        #     self.on_5sec_rtb(data["real_time_bars"])
        # if data.get("bars"):
        #     pass

    def _req_bar_history(self):
        message = {"req": "bar_history"}
        self._send_msg(message)

    def _req_market_data(self):
        message = {"req": "real_market_data"}
        self._send_msg(message)

    def _req_option_details(self):
        message = {"req": "option_details"}
        self._send_msg(message)

    def _req_real_time_bars(self):
        message = {"req": "real_time_bars"}
        self._send_msg(message)

    def _req_tick_by_tick_data(self):
        message = {"req": "tick_by_tick_data"}
        self._send_msg(message)

    def _send_bar_sizes(self):
        message = {"set": {"bar_sizes": self.bar_sizes}}
        self._send_msg(message)

    def _send_tickers(self):
        message = {"set": {"tickers": self.security}}
        self._send_msg(message)

    def _send_msg(self, message):
        msg = ipc.Message(message)
        self.socket_client.send(msg.to_json())


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
