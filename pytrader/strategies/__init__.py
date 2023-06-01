"""!@package pytrader.strategies

Provides the Base Class for a Strategy.

@author G S derber
@version HEAD
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

@file pytrader/strategies/__init__.py

    Provides the Base Class for a Strategy

"""
# System libraries
import datetime

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
    """!
    The strategy class.

    Provides functionality required by strategies.
    """
    __metaclass__ = ABCMeta

    def __init__(self, cmd_queue, data_queue):
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue

        self.time_now = datetime.datetime.now()
        self.contracts = {}
        self.bars = {}
        self.ticks = {}

        self.expirations = {}
        self.all_strikes = {}
        self.strikes = {}

        self.opening_prices = {}

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
    def on_ask(self, ticker, tick):
        pass

    @abstractmethod
    def on_ask_size(self, ticker, tick):
        pass

    @abstractmethod
    def on_average_volume(self, ticker, tick):
        pass

    @abstractmethod
    def on_bar(self):
        pass

    @abstractmethod
    def on_bid(self):
        pass

    @abstractmethod
    def on_bid_size(self):
        pass

    @abstractmethod
    def on_call_open_interest(self):
        pass

    @abstractmethod
    def on_close(self):
        pass

    @abstractmethod
    def on_end(self):
        pass

    @abstractmethod
    def on_halt(self, ticker):
        pass

    @abstractmethod
    def on_high(self):
        pass

    @abstractmethod
    def on_index_future_premium(self):
        pass

    @abstractmethod
    def on_last(self):
        pass

    @abstractmethod
    def on_last_size(self):
        pass

    @abstractmethod
    def on_low(self):
        pass

    @abstractmethod
    def on_mark(self):
        pass

    @abstractmethod
    def on_open(self):
        pass

    @abstractmethod
    def on_option_historical_volatility(self, ticker, tick):
        pass

    @abstractmethod
    def on_option_implied_volatility(self, ticker, tick):
        pass

    @abstractmethod
    def on_put_open_interest(self):
        pass

    @abstractmethod
    def on_shortable(self, ticker, tick):
        pass

    @abstractmethod
    def on_start(self):
        pass

    @abstractmethod
    def on_tick(self):
        pass

    @abstractmethod
    def on_volume(self):
        pass

    def run(self):
        logger.debug("Begin Function")

        try:
            self._create_contracts()
            self._send_contracts()

            #self._send_bar_sizes()
            #self._req_bar_history()

            logger.debug("Use Options: %s", self.use_options)
            #if self.use_options:
            #    self._req_option_details()

            #self._req_real_time_bars()
            #self._req_tick_by_tick_data()
            #self._req_market_data()

            #self.on_start()

            # continue_strategy = True
            # while continue_strategy:
            #     message = self.data_queue.get()
            #     self._process_message(message)
            #     continue_strategy = self.continue_strategy()

        finally:
            self.on_end()

        logger.debug("End Function")

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
                           contract,
                           order_type,
                           price=None,
                           profit_target=None,
                           stop_loss=None):

        ticker = contract.localSymbol

        order = {
            "contract": contract,
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

    def cancel_orders(self, order_id: int = 0):
        if order_id == 0:
            self._req_global_cancel()
        else:
            logger.error("Order Cancelation not implemented")

    def select_option_strikes(self, ticker, price):
        if ticker in self.security:
            x = 0
            y = 1

            logger.debug("Price: %s", str(price))
            price_f = float(price)

            num_strikes = self.num_strikes // 2

            try:
                strikes_len = len(self.all_strikes[ticker])

                while y < strikes_len:

                    lower_price = float(self.all_strikes[ticker][x])
                    upper_price = float(self.all_strikes[ticker][y])

                    if lower_price <= price_f <= upper_price:
                        begin_ = x - num_strikes
                        end_ = y + num_strikes

                        if begin_ < 0:
                            begin_ = 0
                        logger.debug3("All strikes for ticker: %s, %s", ticker,
                                      self.all_strikes[ticker])
                        self.strikes[ticker] = self.all_strikes[ticker][
                            begin_:end_]

                    x += 1
                    y += 1

                logger.debug("Ticker: '%s', Strikes: %s", ticker,
                             self.strikes[ticker])

            except KeyError as msg:
                logger.error("Missing key: %s", ticker)
                logger.error("All Strikes: %s", self.all_strikes)
                logger.error("Error Message: %s", msg)

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _create_contract(self,
                         ticker,
                         sec_type: str = "STK",
                         exchange: str = "SMART",
                         currency: str = "USD",
                         expiry: str = "",
                         strike: float = 0.0,
                         right: str = ""):
        """!
        Creates a contract
        """
        contract_ = contract.Contract()
        contract_.symbol = ticker
        contract_.secType = sec_type
        contract_.exchange = exchange
        contract_.currency = currency

        if expiry != "":
            contract_.lastTradeDateOrContractMonth = expiry
            contract_.multiplier = "100"

        if float(strike) > 0.0:
            contract_.strike = strike

        if right != "":
            contract_.right = right

        return contract_

    def _create_contracts(self):
        for item in self.security:
            self.contracts[item] = self._create_contract(item)

        logger.debug("Contracts: %s", self.contracts)

    def _create_option_contracts(self, ticker):
        contracts = {}

        logger.debug("Ticker: %s", ticker)
        logger.debug("Tickers: %s", self.strikes.keys())

        if ticker in self.security:
            try:
                for strike in self.strikes[ticker]:
                    for right in ["CALL", "PUT"]:
                        contract_name = self._gen_option_contract_name(
                            ticker, right, strike)
                        contracts[contract_name] = self._create_contract(
                            ticker, "OPT", "SMART", "USD",
                            self.expirations[ticker], strike, right)
            except KeyError as msg:
                logger.error("Key '%s' not in '%s': '%s'", ticker,
                             self.strikes.keys(), msg)

        self._send_contracts(contracts)

    def _gen_option_contract_name(self, ticker: str, right: str,
                                  strike: float):
        strike_left = str(strike).split(".")[0]
        strike_right = str(strike).split(".")[1]

        strike_str = strike_left.rjust(5, "0") + strike_right.ljust(3, "0")
        local_symbol = ticker.ljust(6, " ")
        contract_name = local_symbol + self.expirations[ticker][-6:] + right[
            0] + strike_str
        return contract_name

    def _process_5sec_rtb(self, bar_data):
        logger.debug("Bar Data: %s", bar_data)
        ticker, bar_size = self._process_bars(bar_data)

        for item in self.bar_sizes:
            new_bar = self.bars[ticker][bar_size].rescale(item)

            if new_bar:
                self.bars[ticker][item].append_bar(new_bar)
                if item == self.bar_sizes[0]:
                    self.on_bar(ticker, item)
            else:
                self.on_5sec_rtb(ticker, bar_data[ticker]["rtb"])

    def _process_bars(self, bar_data):
        logger.debug("Begin Function")

        # FIXME: There should only be the one key, I shouldn't need to loop this.
        ticker = None
        for ticker, bar_size_dict in bar_data.items():
            logger.debug("Ticker: %s", ticker)
            if ticker not in self.bars.keys():
                self.bars[ticker] = {}

            # FIXME: Again there should only be one key.
            for bar_size, bar_list in bar_size_dict.items():
                logger.debug("Bar Size: %s", bar_size)
                logger.debug("Bar List: %s", bar_list)
                if bar_size in self.bars[ticker].keys():
                    self.bars[ticker][bar_size].append_bar(bar_list)
                else:
                    self.bars[ticker][bar_size] = bars.Bars(bar_size=bar_size,
                                                            bar_list=bar_list)

        return ticker, bar_size

        logger.debug("End Function")

    def _process_data(self, data):
        if data.get("contracts"):
            self.contracts = data["contracts"]
            logger.debug("Contracts: %s", self.contracts)
        if data.get("option_details"):
            logger.debug("Processing Option Details")
            self._process_option_details(data["option_details"])
        if data.get("real_time_bars"):
            logger.debug("Processing Real Time Bars")
            self._process_5sec_rtb(data["real_time_bars"])
        if data.get("bars"):
            logger.debug("Processing Bars")
            self._process_bars(data["bars"])
        if data.get("tick"):
            logger.debug("Processing Tick Data")
            self._process_ticks(data["tick"])
        if data.get("market_data"):
            logger.debug("Processing Market Data")
            self._process_market_data(data["market_data"])

    def _process_message(self, message):

        logger.debug("Message: %s", message)
        if isinstance(message, dict):
            self._process_data(message)
        else:
            # We have an informational message
            logger.info(message)

    def _process_market_data(self, new_market_data):
        logger.debug("Begin Function")

        ticker = None

        for ticker, market_data in new_market_data.items():
            if market_data[0] == "tick_price":
                self._process_mkt_tick_price(ticker, market_data)
            elif market_data[0] == "tick_generic":
                self._process_mkt_tick_generic(ticker, market_data)
            else:
                logger.error(
                    "Processing for tick type '%s' for ticker '%s' has not been implemented.",
                    market_data[0], ticker)
                logger.error("Market Data: %s", market_data)

    def _process_mkt_tick_generic(self, ticker, market_data):
        func_map = {
            23: self.on_option_historical_volatility,
            24: self.on_option_implied_volatility,
            31: self.on_index_future_premium,
            46: self.on_shortable,
            49: self.on_halt
        }

        if market_data[1] in func_map.keys():
            func = func_map.get(market_data[1])
            func(ticker, market_data[2])
        else:
            logger.warning("Market Data Type Id #%s has not been implemented",
                           market_data[1])
            logger.warning("Market Data for Ticker %s: %s", ticker,
                           market_data)

    def _process_mkt_tick_price(self, ticker, market_data):
        func_map = {
            1: self.on_bid,
            2: self.on_ask,
            4: self.on_last,
            6: self.on_high,
            7: self.on_low,
            9: self.on_close,
            14: self.on_open,
            37: self.on_mark
        }
        logger.debug6("Func Map: %s", func_map)
        logger.debug5("Tick Type ID: %s", market_data[1])
        logger.debug4("Broker Function: %s", func_map.get(market_data[1]))

        # Until we have all tick types defined at:
        # https://interactivebrokers.github.io/tws-api/tick_types.html
        # we will need this 'if' statement.
        if market_data[1] == 14:
            # We really only want to run this one time.
            if ticker not in self.opening_prices.keys():
                #self._select_strikes()

                self.opening_prices[ticker] = market_data
                func = func_map.get(market_data[1])
                func(ticker, market_data[2])

        elif market_data[1] in func_map.keys():
            func = func_map.get(market_data[1])
            func(ticker, market_data[2])
        else:
            logger.error("Market Data Type Id #%s has not been implemented",
                         market_data[1])
            logger.error("Market Data for Ticker %s: %s", ticker, market_data)

    def _process_mkt_tick_size(self, ticker, market_data):
        func_map = {
            0: self.on_bid_size,
            3: self.on_ask_size,
            5: self.on_last_size,
            8: self.on_volume,
            21: self.on_average_volume,
            27: self.on_call_open_interest,
            28: self.on_put_open_interest
        }

        if market_data[1] in func_map.keys():
            func = func_map.get(market_data[1])
            func(ticker, market_data[2])
            logger.debug("Market Data for Ticker %s: %s", ticker, market_data)

        else:
            logger.error("Market Data Type Id #%s has not been implemented",
                         market_data[1])
            logger.error("Market Data for Ticker %s: %s", ticker, market_data)

    def _process_option_details(self, option_details):
        ticker = option_details["ticker"]
        details = option_details["details"]
        expirations = list(details["expirations"])
        strikes = list(details["strikes"])
        expirations.sort()
        strikes.sort()
        self._select_expiration(ticker, expirations)
        self.all_strikes[ticker] = strikes

    def _process_ticks(self, new_ticks):
        logger.debug("Begin Function")
        ticker = None
        for ticker, tick in new_ticks.items():
            if ticker not in self.ticks.keys():
                self.ticks[ticker] = ticks.Ticks()

            self.ticks[ticker].append_tick(tick)
            self.on_tick(ticker, tick)

        logger.debug("End Function")

    def _req_bar_history(self):
        message = {"req": "bar_history"}
        self.cmd_queue.put(message)

    def _req_global_cancel(self):
        message = {"req": "global_cancel"}
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

    def _select_expiration(self, ticker, expirations):
        logger.debug3("Expirations List: %s", expirations)
        min_expiry = datetime.datetime.today() + datetime.timedelta(
            days=self.days_to_expiration)

        # We want to make sure we are checking based on midnight of the day
        min_expiry = datetime.datetime.combine(min_expiry,
                                               datetime.datetime.min.time())
        logger.debug2("Earliest Expiry for ticker %s: %s", ticker, min_expiry)

        expiry_date = datetime.datetime(year=1970, month=1, day=1)

        while expiry_date < min_expiry:
            item = expirations.pop(0)
            expiry_date = datetime.datetime.strptime(item, "%Y%m%d")
            self.expirations[ticker] = item

        logger.debug("Ticker '%s', Expiry '%s'", ticker, expiry_date)

    #def _select_strikes(self):

    def _send_order(self, order):
        message = {"place_order": order}
        self.cmd_queue.put(message)

    def _send_bar_sizes(self):
        message = {"set": {"bar_sizes": self.bar_sizes}}
        self.cmd_queue.put(message)

    def _send_contracts(self, contracts: dict = {}):
        if contracts:
            contracts_to_send = contracts
        else:
            contracts_to_send = self.contracts

        if contracts is False:
            logger.error("Contracts Not Set")

        message = {"set": {"tickers": contracts_to_send}}
        self.cmd_queue.put(message)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
