"""!@package pytrader.strategies

Provides the Base Class for a Strategy.

@author G. S. derber
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
from multiprocessing import Queue

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

    def __init__(self, cmd_queue: Queue, data_queue: Queue, next_order_id: int, strategy_id: str):
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue
        self.next_order_id = next_order_id
        self.strategy_id = strategy_id

        self.time_now = datetime.datetime.now()

        self.security = []
        self.use_options = False
        self.quantity = 0
        self.num_strikes = 0
        self.bar_sizes = []
        self.days_to_expiration = 0

        self.contracts = {}
        self.bars = {}
        self.ticks = {}
        self.market_data = {}
        self.orders = {}
        self.order_ids = {}
        self.order_prices = {}

        self.expirations = {}
        self.all_strikes = {}
        self.strikes = {}

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
    def on_5sec_rtb(self, ticker, bar):
        pass

    @abstractmethod
    def on_3min_volume(self, ticker, tick):
        pass

    @abstractmethod
    def on_5min_volume(self, ticker, tick):
        pass

    @abstractmethod
    def on_10min_volume(self, ticker, tick):
        pass

    @abstractmethod
    def on_13week_high(self, ticker, tick):
        pass

    @abstractmethod
    def on_13week_low(self, ticker, tick):
        pass

    @abstractmethod
    def on_26week_high(self, ticker, tick):
        pass

    @abstractmethod
    def on_26week_low(self, ticker, tick):
        pass

    @abstractmethod
    def on_52week_high(self, ticker, tick):
        pass

    @abstractmethod
    def on_52week_low(self, ticker, tick):
        pass

    @abstractmethod
    def on_ask(self, ticker, tick):
        pass

    @abstractmethod
    def on_ask_exchange(self, ticker, tick):
        pass

    @abstractmethod
    def on_ask_option_computation(self, ticker, tick):
        pass

    @abstractmethod
    def on_ask_size(self, ticker, tick):
        pass

    @abstractmethod
    def on_auction_imbalance(self, ticker, tick):
        pass

    @abstractmethod
    def on_auction_price(self, ticker, tick):
        pass

    @abstractmethod
    def on_auction_volume(self, ticker, tick):
        pass

    @abstractmethod
    def on_average_option_volume(self, ticker, tick):
        pass

    @abstractmethod
    def on_average_volume(self, ticker, tick):
        pass

    @abstractmethod
    def on_bar(self, ticker, bar_size):
        pass

    @abstractmethod
    def on_bid(self, ticker, tick):
        pass

    @abstractmethod
    def on_bid_exchange(self, ticker, tick):
        pass

    @abstractmethod
    def on_bid_option_computation(self, ticker, tick):
        pass

    @abstractmethod
    def on_bid_size(self, ticker, tick):
        pass

    @abstractmethod
    def on_close(self, ticker, tick):
        pass

    @abstractmethod
    def on_creditman_slow_mark_price(self, ticker, tick):
        pass

    @abstractmethod
    def on_dividends(self, ticker, tick):
        pass

    @abstractmethod
    def on_end(self):
        pass

    @abstractmethod
    def on_halt(self, ticker, tick):
        pass

    @abstractmethod
    def on_high(self, ticker, tick):
        pass

    @abstractmethod
    def on_last(self, ticker, tick):
        pass

    @abstractmethod
    def on_last_exchange(self, ticker, tick):
        pass

    @abstractmethod
    def on_last_option_computation(self, ticker, tick):
        pass

    @abstractmethod
    def on_last_rth_trade(self, ticker, tick):
        pass

    @abstractmethod
    def on_last_size(self, ticker, tick):
        pass

    @abstractmethod
    def on_last_timestamp(self, ticker, tick):
        pass

    @abstractmethod
    def on_low(self, ticker, tick):
        pass

    @abstractmethod
    def on_mark(self, ticker, tick):
        pass

    @abstractmethod
    def on_model_option_computation(self, ticker, tick):
        pass

    @abstractmethod
    def on_news(self, ticker, tick):
        pass

    @abstractmethod
    def on_open(self, ticker, tick):
        pass

    @abstractmethod
    def on_option_historical_volatility(self, ticker, tick):
        pass

    @abstractmethod
    def on_option_implied_volatility(self, ticker, tick):
        pass

    @abstractmethod
    def on_option_call_open_interest(self, ticker, tick):
        pass

    @abstractmethod
    def on_option_put_open_interest(self, ticker, tick):
        pass

    @abstractmethod
    def on_option_call_volume(self, ticker, tick):
        pass

    @abstractmethod
    def on_option_put_volume(self, ticker, tick):
        pass

    @abstractmethod
    def on_order_cancelled(self, local_symbol, order_id, order_status):
        pass

    @abstractmethod
    def on_order_filled(self, local_symbol, order_id, order_status):
        pass

    @abstractmethod
    def on_rt_volume(self, ticker, tick):
        pass

    @abstractmethod
    def on_rt_trade_volume(self, ticker, tick):
        pass

    @abstractmethod
    def on_shortable(self, ticker, tick):
        pass

    @abstractmethod
    def on_shortable_shares(self, ticker, tick):
        pass

    @abstractmethod
    def on_start(self):
        pass

    @abstractmethod
    def on_tick(self, ticker, tick):
        pass

    @abstractmethod
    def on_trade_count(self, ticker, tick):
        pass

    @abstractmethod
    def on_trade_rate(self, ticker, tick):
        pass

    @abstractmethod
    def on_volume(self, ticker, tick):
        pass

    @abstractmethod
    def on_volume_per_minute(self, ticker, tick):
        pass

    def run(self):
        logger.debug10("Begin Function")

        try:
            self._create_contracts()
            self._send_contracts()

            self._send_bar_sizes()

            logger.debug9("Use Options: %s", self.use_options)
            if self.use_options:
                self._req_option_details()

            self._req_bar_history()

            self._req_real_time_bars()
            #self._req_tick_by_tick_data()
            self._req_market_data()

            self.on_start()

            continue_strategy = True
            while continue_strategy:
                message = self.data_queue.get()
                self._process_message(message)
                continue_strategy = self.continue_strategy()

        except KeyboardInterrupt as msg:
            logger.critical("Received Keyboard Interupt, shutting down now!")
        # except Exception as msg:
        #     logger.critical("We fucked up: %s", msg)

        finally:
            self.on_end()

    def cancel_orders(self, order_id: int = 0):
        if order_id == 0:
            self._req_global_cancel()
        else:
            logger.warning("Order Cancelation not implemented")

    def select_options(self, ticker, tick):
        if self.use_options:
            if not self.strikes.get(ticker):
                self.select_option_strikes(ticker, tick)
                self._create_option_contracts(ticker)

                # Re-send requests to get data for options as well
                self._send_bar_sizes()
                self._req_bar_history()
                self._req_real_time_bars()
                self._req_market_data()

    def select_option_strikes(self, ticker, price):
        x = 0
        y = 1

        if ticker in self.security:

            logger.debug9("Price: %s", str(price))
            price_f = float(price)

            num_strikes = self.num_strikes // 2

            strikes_len = len(self.all_strikes[ticker])

            while y < strikes_len:

                lower_price = float(self.all_strikes[ticker][x])
                upper_price = float(self.all_strikes[ticker][y])

                if lower_price <= price_f <= upper_price:
                    begin_ = x - num_strikes
                    end_ = y + num_strikes

                    begin_ = max(begin_, 0)
                    logger.debug9("All strikes for ticker: %s, %s", ticker,
                                  self.all_strikes[ticker])
                    self.strikes[ticker] = self.all_strikes[ticker][begin_:end_]

                x += 1
                y += 1

            logger.debug2("Selected Strikes for %s: %s", ticker, self.strikes[ticker])

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
            self.orders[item] = {}

        logger.debug9("Contracts: %s", self.contracts)

    def _create_option_contracts(self, ticker):
        contracts = {}

        if ticker in self.security:
            for strike in self.strikes[ticker]:
                for right in ["CALL", "PUT"]:
                    contract_name = self._gen_option_contract_name(ticker, right, strike)
                    contracts[contract_name] = self._create_contract(ticker, "OPT", "SMART", "USD",
                                                                     self.expirations[ticker],
                                                                     strike, right)

            self._send_contracts(contracts)

    def _gen_option_contract_name(self, ticker, right, strike):
        strike_left = str(strike).split(".")[0]
        strike_right = str(strike).split(".")[1]

        strike_str = strike_left.rjust(5, "0") + strike_right.ljust(3, "0")
        local_symbol = ticker.ljust(6, " ")
        option_name = local_symbol + self.expirations[ticker][-6:] + right[0] + strike_str
        return option_name

    def _process_5sec_rtb(self, bar_data):
        logger.debug9("Bar Data: %s", bar_data)
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
        # TODO: This is an ugly way to extract key value pairs for dicts with single item

        ticker = list(bar_data.keys())[0]
        bar_size_dict = bar_data[ticker]

        if ticker not in list(self.bars.keys()):
            self.bars[ticker] = {}

        bar_size = list(bar_size_dict.keys())[0]
        bar_list = bar_size_dict[bar_size]

        if bar_size != "rtb":
            logger.debug2("%s Bars received for: %s", bar_size, ticker)
        if bar_size in list(self.bars[ticker].keys()):
            self.bars[ticker][bar_size].append_bar(bar_list)
        else:
            self.bars[ticker][bar_size] = bars.Bars(ticker, bar_size=bar_size, bar_list=bar_list)

            self.bars[ticker][bar_size].create_dataframe()

        return ticker, bar_size

    def _process_contracts(self, contracts):
        self.contracts = contracts
        logger.debug9("Contracts: %s", self.contracts)

        for item in list(self.contracts.keys()):
            self.market_data[item] = {
                "bid": 0,
                "ask": 0,
                "last": 0,
                "open": 0,
                "high": 0,
                "low": 0,
                "close": 0,
                "mark": 0
            }

    def _process_data(self, data: dict):
        if data.get("contracts"):
            self._process_contracts(data["contracts"])
        if data.get("option_details"):
            logger.debug9("Processing Option Details")
            self._process_option_details(data["option_details"])
        if data.get("real_time_bars"):
            logger.debug9("Processing Real Time Bar")
            self._process_5sec_rtb(data["real_time_bars"])
        if data.get("bars"):
            logger.debug9("Processing Bars")
            self._process_bars(data["bars"])
        if data.get("tick"):
            logger.debug9("Processing Tick Data")
            self._process_ticks(data["tick"])
        if data.get("market_data"):
            logger.debug9("Processing Market Data")
            self._process_market_data(data["market_data"])
        if data.get("order_status"):
            logger.debug9("Processing Order Status")
            self._process_order_status(data["order_status"])

    def _process_message(self, message):

        logger.debug9("Message: %s", message)
        if isinstance(message, dict):
            self._process_data(message)
        else:
            # We have an informational message
            logger.debug9("Informational Message exists: %s", message)

    def _process_market_data(self, new_market_data):
        ticker = None

        for ticker, market_data in new_market_data.items():
            # Possible items for list: "tick_price", "tick_size", "tick_string", "tick_generic"
            if market_data[0] in [
                    "tick_price", "tick_size", "tick_string", "tick_option_computation",
                    "tick_generic", "tick_efp"
            ]:
                self._process_mkt_tick_price(ticker, market_data)
            elif market_data[0] == "tick_news":
                self.on_news(ticker, market_data[2])

    def _process_mkt_tick_price(self, ticker, market_data):
        """!
        Uses market data to select function to run.

        @param ticker:
        @param market_data:

        @return None
        """
        func_map = {
            0: self.on_bid_size,
            1: self.on_bid,
            2: self.on_ask,
            3: self.on_ask_size,
            4: self.on_last,
            5: self.on_last_size,
            6: self.on_high,
            7: self.on_low,
            8: self.on_volume,
            9: self.on_close,
            10: self.on_bid_option_computation,
            11: self.on_ask_option_computation,
            12: self.on_last_option_computation,
            13: self.on_model_option_computation,
            14: self.on_open,
            15: self.on_13week_low,
            16: self.on_13week_high,
            17: self.on_26week_low,
            18: self.on_26week_high,
            19: self.on_52week_low,
            20: self.on_52week_high,
            21: self.on_average_volume,
            23: self.on_option_historical_volatility,
            24: self.on_option_implied_volatility,
            27: self.on_option_call_open_interest,
            28: self.on_option_put_open_interest,
            29: self.on_option_call_volume,
            30: self.on_option_put_volume,
            32: self.on_bid_exchange,
            33: self.on_ask_exchange,
            34: self.on_auction_volume,
            35: self.on_auction_price,
            36: self.on_auction_imbalance,
            37: self.on_mark,
            45: self.on_last_timestamp,
            46: self.on_shortable,
            48: self.on_rt_volume,
            49: self.on_halt,
            54: self.on_trade_count,
            55: self.on_trade_rate,
            56: self.on_volume_per_minute,
            57: self.on_last_rth_trade,
            59: self.on_dividends,
            63: self.on_3min_volume,
            64: self.on_5min_volume,
            65: self.on_10min_volume,
            84: self.on_last_exchange,
            77: self.on_rt_trade_volume,
            79: self.on_creditman_slow_mark_price,
            87: self.on_average_option_volume,
            89: self.on_shortable_shares
        }
        data_map = {
            0: "bid_size",
            1: "bid",
            2: "ask",
            3: "ask_size",
            4: "last",
            5: "last_size",
            6: "high",
            7: "low",
            8: "volume",
            9: "close",
            10: "bid_option_computation",
            11: "ask_option_computation",
            12: "last_option_computation",
            13: "model_option_computation",
            14: "open",
            15: "13week_low",
            16: "13week_high",
            17: "26week_low",
            18: "26week_high",
            19: "52week_low",
            20: "52week_high",
            21: "average_volume",
            23: "option_historical_volatility",
            24: "option_implied_volatility",
            27: "option_call_open_interest",
            28: "option_put_open_interest",
            29: "option_call_volume",
            30: "option_put_volume",
            32: "bid_exchange",
            33: "ask_exchange",
            34: "auction_volume",
            35: "auction_price",
            36: "auction_imbalance",
            37: "mark",
            45: "last_timestamp",
            46: "shortable",
            48: "rt_volume",
            49: "halted",
            54: "trade_count",
            55: "trade_rate",
            56: "volume_per_minute",
            57: "last_rth_trade",
            59: "dividends",
            63: "3min_volume",
            64: "5min_volume",
            65: "10min_volume",
            84: "last_exchange",
            77: "rt_trade_volume",
            79: "creditman_slow_mark_price",
            87: "average_option_volume",
            89: "shortable_shares"
        }

        logger.debug9("Func Map: %s", func_map)
        logger.debug9("Tick Type ID: %s", market_data[1])
        logger.debug9("Broker Function: %s", func_map.get(market_data[1]))

        market_close = datetime.datetime.combine(datetime.date.today(),
                                                 datetime.time(hour=16, minute=0))
        market_close_min1 = datetime.datetime.combine(datetime.date.today(),
                                                      datetime.time(hour=15, minute=59))

        cur_time = datetime.datetime.now()

        if cur_time > market_close:
            logger.critical("Market Data Type Id #%s", market_data[1])
        elif cur_time > market_close_min1:
            logger.warning("Market Data Type Id #%s", market_data[1])

        # Until we have all tick types defined at:
        # https://interactivebrokers.github.io/tws-api/tick_types.html
        # we will need this 'if' statement.
        if market_data[1] == 14:
            # We really only want to run 'on_open' function one time, while we may received the data
            # multiple times.
            if self.market_data[ticker]["open"] == 0:
                self.market_data[ticker]["open"] = market_data[2]
                func = func_map.get(market_data[1])
                func(ticker, market_data[2])
        elif market_data[1] in list(func_map.keys()):
            func = func_map.get(market_data[1])
            func(ticker, market_data[2])
            self.market_data[ticker][data_map[market_data[1]]] = market_data[2]
            logger.debug9("Market Data for ticker %s: %s", ticker, self.market_data[ticker])
        else:
            logger.warning("Market Data Type Id #%s has not been implemented.  Ticker %s, Data %s",
                           market_data[1], ticker, market_data)

    def _process_option_details(self, option_details):
        ticker = option_details["ticker"]
        details = option_details["details"]
        expirations = list(details["expirations"])
        strikes = list(details["strikes"])
        expirations.sort()
        strikes.sort()
        self._select_expiration(ticker, expirations)
        self.all_strikes[ticker] = strikes

    def _process_order_status(self, order_status):
        logger.debug8("Order Status: %s", order_status)
        order_id = list(order_status.keys())[0]

        if order_id in order_status.keys():
            status = order_status[order_id]["status"]
            local_symbol = self.order_ids[order_id]

            func_map = {
                "Filled": self.on_order_filled,
                "Cancelled": self.on_order_cancelled,
                "ApiCancelled": self.on_order_cancelled,
                "TWS_CLOSED": self.on_order_cancelled
            }

            if order_id in list(self.order_ids.keys()):

                if status in ["Filled", "Cancelled", "ApiCancelled"]:
                    logger.debug9("Order %s to be removed", order_id)
                    self.orders[local_symbol].pop(order_id, None)
                else:
                    if order_id in list(self.orders[local_symbol].keys()):
                        self.orders[local_symbol][order_id].set_status(status)
                        logger.debug9("Order Status: %s",
                                      self.orders[local_symbol][order_id].get_status())

                    else:
                        logger.debug9("Orders for %s", local_symbol)
                        logger.debug9("Orders: %s", self.orders[local_symbol])

            #func = func_map.get(status)
            #func(local_symbol, order_id, order_status[order_id])

    def _process_ticks(self, new_ticks):
        ticker = None
        for ticker, tick in new_ticks.items():
            if ticker not in list(self.ticks.keys()):
                self.ticks[ticker] = ticks.Ticks()

            self.ticks[ticker].append_tick(tick)
            self.on_tick(ticker, tick)

        logger.debug10("End Function")

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
        logger.debug9("Expirations List: %s", expirations)
        min_expiry = datetime.datetime.today() + datetime.timedelta(days=self.days_to_expiration)

        # We want to make sure we are checking based on midnight of the day
        min_expiry = datetime.datetime.combine(min_expiry, datetime.datetime.min.time())
        logger.debug9("Earliest Expiry: %s", min_expiry)

        expiry_date = datetime.datetime(year=1970, month=1, day=1)

        while expiry_date < min_expiry:
            item = expirations.pop(0)
            expiry_date = datetime.datetime.strptime(item, "%Y%m%d")
            self.expirations[ticker] = item

        logger.debug2("Expiry for %s: %s", ticker, expiry_date)

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
