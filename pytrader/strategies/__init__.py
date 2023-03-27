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
import json

from abc import ABCMeta, abstractmethod

# 3rd Party libraries
from ibapi import order

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs import bars
from pytrader.libs import ticks
from pytrader.libs.utilities import ipc

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
        self.bars = {}
        self.ticks = {}

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
    def on_5sec_rtb(self):
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
            self._req_tick_by_tick_data()
            #self._req_market_data()

            continue_strategy = True
            while continue_strategy:
                message = self.socket_client.recv()
                self._process_data(message)
                continue_strategy = self.continue_strategy()

        finally:
            #self.on_end()
            self.socket_client.disconnect()

        # bar_adjustment = self._bar_conversion()

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
    def _process_5sec_rtb(self, bar_data):
        logger.debug2("Bar Data: %s", bar_data)
        ticker, bar_size = self._process_bars(bar_data)

        for item in self.bar_sizes:
            new_bar = self.bars[ticker][bar_size].rescale(item)

            if new_bar:
                self.bars[ticker][item].append_bar(new_bar)
                if item == self.bar_sizes[0]:
                    self.on_bar(ticker, item)
            else:
                self.on_5sec_rtb()

    def _process_bars(self, bar_data):
        logger.debug10("Begin Function")
        # FIXME: There should only be the one key, I shouldn't need to loop this.
        ticker = None
        for ticker, bar_size_dict in bar_data.items():
            logger.debug3("Ticker: %s", ticker)
            if ticker not in self.bars.keys():
                self.bars[ticker] = {}

            # FIXME: Again there should only be one key.
            for bar_size, bar_list in bar_size_dict.items():
                logger.debug3("Bar Size: %s", bar_size)
                logger.debug4("Bar List: %s", bar_list)
                if bar_size in self.bars[ticker].keys():
                    self.bars[ticker][bar_size].append_bar(bar_list)
                else:
                    self.bars[ticker][bar_size] = bars.Bars(bar_size=bar_size,
                                                            bar_list=bar_list)

        return ticker, bar_size

        logger.debug10("End Function")

    def _process_data(self, message):

        # WTF! I really don't like this way of skipping over confirmation messages.
        logger.debug4("Message: %s", message)
        try:
            data = json.loads(message)
        except Exception as exception_msg:
            logger.warning("Invalid JSON, Message: '%s', Error Msg: '%s'",
                           message, exception_msg)
            data = {}

        if data.get("real_time_bars"):
            logger.debug3("Processing Real Time Bars")
            self._process_5sec_rtb(data["real_time_bars"])
        if data.get("bars"):
            logger.debug3("Processing Bars")
            self._process_bars(data["bars"])

        if data.get("tick"):
            logger.debug("Processing Tick Data")
            self._process_ticks(data["tick"])

    def _process_ticks(self, new_ticks):
        logger.debug10("Begin Function")
        ticker = None
        for ticker, tick in new_ticks.items():
            if ticker not in self.ticks.keys():
                self.ticks[ticker] = ticks.Ticks()

            self.ticks[ticker].append_tick(tick)
            self.on_tick(ticker, tick)

    def _req_bar_history(self):
        message = {"req": "bar_history"}
        self._send_msg(message)

    def _req_market_data(self):
        message = {"req": "realtime_market_data"}
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
