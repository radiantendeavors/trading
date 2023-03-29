"""!@package pytrader.strategies

Provides the Base Class for a Strategy.

@author G S derber
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

@file pytrader/strategies/__init__.py

    Provides the Base Class for a Strategy

"""
# System libraries
import datetime
import json

from abc import ABCMeta, abstractmethod

# 3rd Party libraries
from ibapi import contract

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs import bars
# from pytrader.libs import contracts
from pytrader.libs import ticks

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base Logger
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Strategy():

    __metaclass__ = ABCMeta

    def __init__(self, cmd_queue, data_queue):
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue

        self.time_now = datetime.datetime.now()
        self.contracts = {}
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
    def on_ask(self):
        pass

    @abstractmethod
    def on_bar(self):
        pass

    @abstractmethod
    def on_bid(self):
        pass

    @abstractmethod
    def on_end(self):
        pass

    @abstractmethod
    def on_high(self):
        pass

    @abstractmethod
    def on_last(self):
        pass

    @abstractmethod
    def on_low(self):
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
            self._send_tickers(self.security)

            self._send_bar_sizes()
            self._req_bar_history()

            logger.debug3("Use Options: %s", self.use_options)
            if self.use_options:
                self._req_option_details()

            self._req_real_time_bars()
            self._req_tick_by_tick_data()
            self._req_market_data()

            continue_strategy = True
            while continue_strategy:
                message = self.data_queue.get()
                self._process_message(message)
                continue_strategy = self.continue_strategy()

        finally:
            self.on_end()

        logger.debug10("End Function")

    def close_long_position(self, ticker, order_type=None, price=None):
        order = {
            "ticker": ticker,
            "order_type": order_type,
            "action": "SELL",
            "quantity": self.quantity
        }

        if order_type is None:
            order_type = "MKT"

        if price:
            order["price"] = price

        self._send_order(order)

    def open_long_position(self,
                           ticker,
                           order_type,
                           price=None,
                           profit_target=None,
                           stop_loss=None):
        order = {
            "ticker": ticker,
            "order_type": order_type,
            "action": "BUY",
            "quantity": self.quantity
        }

        if price:
            order["price"] = price
        if profit_target:
            order["profit_target"] = profit_target
        if stop_loss:
            order["stop_loss"] = stop_loss

        self._send_order(order)
        self.long_position.append(ticker)

    def open_short_position(self,
                            ticker,
                            order_type,
                            price=None,
                            profit_target=None,
                            stop_loss=None):
        order = {
            "ticker": ticker,
            "order_type": order_type,
            "action": "SELL",
            "quantity": self.quantity
        }

        if price:
            order["price"] = price
        if profit_target:
            order["profit_target"] = profit_target
        if stop_loss:
            order["stop_loss"] = stop_loss

        self._send_order(order)
        self.short_position.append(ticker)

    def close_short_position(self, ticker, order_type=None, price=None):
        order = {
            "ticker": ticker,
            "order_type": order_type,
            "action": "BUY",
            "quantity": self.quantity
        }
        if order_type is None:
            order_type = "MKT"

        if price:
            order["price"] = price

        self._send_order(order)

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _process_5sec_rtb(self, bar_data):
        logger.debug3("Bar Data: %s", bar_data)
        ticker, bar_size = self._process_bars(bar_data)

        for item in self.bar_sizes:
            new_bar = self.bars[ticker][bar_size].rescale(item)

            if new_bar:
                self.bars[ticker][item].append_bar(new_bar)
                if item == self.bar_sizes[0]:
                    self.on_bar(ticker, item)
            else:
                self.on_5sec_rtb(ticker, item)

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

    def _process_data(self, data):
        if data.get("contracts"):
            self.contracts = data["contracts"]
            logger.debug("Contracts: %s", self.contracts)
        if data.get("real_time_bars"):
            logger.debug3("Processing Real Time Bars")
            self._process_5sec_rtb(data["real_time_bars"])
        if data.get("bars"):
            logger.debug3("Processing Bars")
            self._process_bars(data["bars"])
        if data.get("tick"):
            logger.debug3("Processing Tick Data")
            self._process_ticks(data["tick"])
        if data.get("market_data"):
            logger.debug3("Processing Market Data")
            self._process_market_data(data["market_data"])

    def _process_message(self, message):

        logger.debug4("Message: %s", message)
        if isinstance(message, dict):
            self._process_data(message)
        else:
            # We have an informational message
            logger.info(message)

    def _process_market_data(self, new_market_data):
        logger.debug10("Begin Function")

        ticker = None

        for ticker, market_data in new_market_data.items():
            if market_data[0] == "tick_price":
                self._process_mkt_tick_price(ticker, market_data)

    def _process_mkt_tick_price(self, ticker, market_data):
        func_map = {
            1: self.on_bid,
            2: self.on_ask,
            4: self.on_last,
            6: self.on_high,
            7: self.on_low
        }
        logger.debug6("Func Map: %s", func_map)
        logger.debug5("Tick Type ID: %s", market_data[1])
        logger.debug4("Broker Subclass: %s", func_map.get(market_data[1]))

        # Until we have all tick types defined at:
        # https://interactivebrokers.github.io/tws-api/tick_types.html
        # we will need this 'if' statement.
        if market_data[1] in func_map.keys():
            func = func_map.get(market_data[1])
            func(ticker, market_data)
        else:
            logger.warning("Market Data Type Id #%s has not been implemented",
                           market_data[1])

    def _process_ticks(self, new_ticks):
        logger.debug10("Begin Function")
        ticker = None
        for ticker, tick in new_ticks.items():
            if ticker not in self.ticks.keys():
                self.ticks[ticker] = ticks.Ticks()

            self.ticks[ticker].append_tick(tick)
            self.on_tick(ticker, tick)

        logger.debug10("End Function")

    def _req_bar_history(self):
        message = {"req": "bar_history"}
        self.cmd_queue.put(message)

    def _req_market_data(self):
        message = {"req": "real_time_market_data"}
        self.cmd_queue.put(message)

    def _req_option_details(self):
        message = {"req": "option_details"}
        self.cmd_queue.put(message)

    def _req_real_time_bars(self):
        message = {"req": "real_time_bars"}
        self.cmd_queue.put(message)

    def _req_tick_by_tick_data(self):
        message = {"req": "tick_by_tick_data"}
        self.cmd_queue.put(message)

    def _send_order(self, order):
        message = {"place_order": order}
        self.cmd_queue.put(message)

    def _send_bar_sizes(self):
        message = {"set": {"bar_sizes": self.bar_sizes}}
        self.cmd_queue.put(message)

    def _send_tickers(self, tickers, sec_type: str = "STK"):
        for item in tickers:
            contract_ = contract.Contract()
            contract_.symbol = item
            contract_.secType = sec_type
            contract_.exchange = "SMART"
            contract_.currency = "USD"
            self.contracts[item] = contract_

        message = {"set": {"tickers": self.contracts}}
        self.cmd_queue.put(message)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
