"""!
@package pytrader.libs.clients.broker.ibkr.tws.twsdemo

Creates the interface for connecting to Tws Demo account.

@author G S Derber
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

@file pytrader/libs/clients/broker/ibkr/tws/twsdemo.py

Creates the interface for connecting to Tws Demo account.
"""
# System Libraries
import datetime
import threading
from time import sleep

# 3rd Party Libraries
from ibapi.contract import Contract

# Application Libraries
from pytrader import CLIENT_ID
from pytrader.libs.clients.broker.abstractclient import AbstractBrokerClient
from pytrader.libs.clients.broker.ibkr.tws import TwsApiClient
from pytrader.libs.system import logging

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## Amount of time to sleep to avoid pacing violations.
HISTORICAL_DATA_SLEEP_TIME = 0

## Sleep time to avoid pacing violations
SMALL_BAR_SLEEP_TIME = 15

## Used to store bar sizes with pacing violations
SMALL_BAR_SIZES = ["1 secs", "5 secs", "10 secs", "15 secs", "30 secs"]

## Used to store allowed intraday bar sizes
INTRADAY_BAR_SIZES = SMALL_BAR_SIZES + [
    "1 min", "2 mins", "3 mins", "5 mins", "10 mins", "15 mins", "20 mins", "30 mins", "1 hour",
    "2 hours", "3 hours", "4 hours", "8 hours"
]

## Used to store allowed bar sizes
BAR_SIZES = INTRADAY_BAR_SIZES + ["1 day", "1 week", "1 month"]

## The Base Logger
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class TwsAccountClient(AbstractBrokerClient):
    """!
    Base Class common to all account types:
      - TwsReal
      - TwsDemo
      - IbgReal
      - IbgDemo
    """
    __next_client_id = CLIENT_ID

    ##
    __contract_details_sleep_time = 0

    ## Used to track when the last contract details data request was made
    __contract_details_data_req_timestamp = datetime.datetime(year=1970,
                                                              month=1,
                                                              day=1,
                                                              hour=0,
                                                              minute=0,
                                                              second=0)

    def __init__(self, data_queue: dict) -> None:
        """!
        Initializes the TwsDataThread class.
        """
        #
        self.brokerclient = TwsApiClient()

        # Contract Subjects and Observers
        self.req_id = 0

        self.brokerclient.set_data_queue(data_queue)

        super().__init__(data_queue)

    def connect(self, address: str = "127.0.0.1", port: int = 0):
        if port == 0:
            port = self.port
        self.brokerclient.connect(address, port, self.__next_client_id)
        self.__next_client_id += 1

    def set_broker_observers(self, broker: str) -> None:
        self.brokerclient.config_broker_observers(broker, self.queue)

    def set_downloader_observers(self) -> None:
        self.brokerclient.config_downloader_observers()

    def set_main_observers(self) -> None:
        self.brokerclient.config_main_observers()

    def set_strategy_observers(self, strategy_list: list) -> None:
        self.brokerclient.config_strategy_observers(strategy_list)

    def start(self):
        self.brokerclient.start()

    def stop(self):
        self.brokerclient.stop()

    def cancel_order(self, order_id: int) -> None:
        """!
        Cancels a specific order.

        @param order_id: The order id to cancel.

        @return None.
        """
        self.order_subjects.cancel_order(order_id)

    def calculate_implied_volatility(self):
        logger.debug("Calculate Implied Volatility")

    def calculate_option_price(self):
        logger.debug("Calculate Option Price")

    def create_order(self, order_request: dict, strategy_id: str) -> None:
        """!
        Create a new order from an order request.

        @param order_request: The details of the order to create.

        @return None.
        """
        order_contract = order_request["contract"]
        new_order = order_request["order"]
        order_id = new_order.orderId

        self.order_subjects.create_order(order_contract, new_order, order_id)
        self.order_observers[strategy_id].add_order_id(order_id)

    def request_bar_history(self) -> None:
        self.bar_subjects.request_bars()
        self.bar_subjects.notify()

    def request_contract_details(self, contract: Contract):
        self.req_id += 1
        self._contract_details_data_wait()
        logger.debug("Contract: %s", contract)
        self.brokerclient.req_contract_details(self.req_id, contract)
        self.__contract_details_data_req_timestamp = datetime.datetime.now()

    def request_global_cancel(self) -> None:
        self.brokerclient.req_global_cancel()

    def request_history_begin_date(self, contract: Contract) -> None:
        self.req_id += 1
        self.brokerclient.contract_history_begin_subjects.add_ticker(self.req_id,
                                                                     contract.localSymbol)
        logger.debug(self.brokerclient.contract_history_begin_subjects)
        self.brokerclient.req_head_timestamp(self.req_id, contract)

    def request_option_details(self, strategy_id):
        tickers = self.contract_observers[strategy_id].get_tickers()
        contracts = self.contract_subjects.get_contracts()

        self.option_observers[strategy_id].add_tickers(tickers)
        self.option_subjects.add_tickers(tickers, contracts)
        self.option_subjects.request_option_details()
        self.option_subjects.notify()

    def request_real_time_bars(self, strategy_id):
        tickers = self.contract_observers[strategy_id].get_tickers()
        contracts = self.contract_subjects.get_contracts()

        self.rtb_observers[strategy_id].add_tickers(tickers)
        self.rtb_subjects.add_tickers(tickers, contracts)
        self.rtb_subjects.request_real_time_bars()

    def request_market_data(self, strategy_id):
        tickers = self.contract_observers[strategy_id].get_tickers()
        contracts = self.contract_subjects.get_contracts()

        self.mkt_data_observers[strategy_id].add_tickers(tickers)
        self.mkt_data_subjects.add_tickers(tickers, contracts)
        self.mkt_data_subjects.request_market_data()

    def send_market_data_ticks(self, market_data: dict):
        self.mkt_data_subjects.send_market_data_ticks(market_data)

    def send_order_status(self, order_status: dict):
        self.order_subjects.send_order_status(order_status)

    def send_real_time_bars(self, real_time_bar: dict):
        self.rtb_subjects.send_real_time_bars(real_time_bar)

    def set_contract_details(self, contract_details: dict):
        self.contract_subjects.set_contract_details(contract_details)

    def set_bar_sizes(self, bar_sizes: list, strategy_id: str):
        """!
        Sets bar sizes

        @param bar_sizes: Bar sizes to use

        @return None
        """
        tickers = self.contract_observers[strategy_id].get_tickers()
        contracts = self.contract_subjects.get_contracts()
        self.bar_subjects.add_bar_sizes(tickers, contracts, bar_sizes)
        self.bar_observers[strategy_id].add_ticker_bar_sizes(tickers, bar_sizes)

    # ==============================================================================================
    #
    # Internal Helper Functions
    #
    # ==============================================================================================
    def _data_wait(self, timestamp, sleep_time):
        time_diff = datetime.datetime.now() - timestamp

        # FIXME: Why is this a loop?
        while time_diff.total_seconds() < sleep_time:

            logger.debug6("Now: %s", datetime.datetime.now())
            logger.debug6("Last Request: %s", timestamp)
            logger.debug6("Time Difference: %s seconds", time_diff.total_seconds())
            remaining_sleep_time = sleep_time - time_diff.total_seconds()
            logger.debug6("Sleep Time: %s", remaining_sleep_time)
            sleep(sleep_time - time_diff.total_seconds())
            time_diff = datetime.datetime.now() - timestamp

    def _historical_data_wait(self):
        """!
        Ensure that we wait between historical data requests.

        @param self

        @return
        """
        self._data_wait(self.__historical_data_req_timestamp, HISTORICAL_DATA_SLEEP_TIME)

    def _req_tick_by_tick_data(self, contract: Contract, tick_type: str, number_of_ticks: int,
                               ignore_size: bool):
        self.req_id += 1
        self._historical_data_wait()

        self.reqTickByTickData(self.req_id, contract, tick_type, number_of_ticks, ignore_size)
        self.__historical_data_req_timestamp = datetime.datetime.now()
        logger.debug("End Function")
        return self.req_id

    def _small_bar_data_wait(self):
        """!
        Ensure that we wait between historical data requests.

        @param self

        @return
        """
        self._data_wait(self.__small_bar_data_req_timestamp, SMALL_BAR_SLEEP_TIME)

    def _contract_details_data_wait(self):
        """!
        Ensure that we wait between historical data requests.

        @param self

        @return
        """
        self._data_wait(self.__contract_details_data_req_timestamp,
                        self.__contract_details_sleep_time)

    def _calculate_deep_data_allotment(self):
        """!
        Caclulates the allowed dep data requests available.
        """
        min_allotment = 3
        max_allotment = 60

        basic_allotment = self.__available_market_data_lines % 100

        if basic_allotment < min_allotment:
            self.__available_deep_data_allotment = min_allotment
        elif basic_allotment > max_allotment:
            self.__available_deep_data_allotment = max_allotment
        else:
            self.__available_deep_data_allotment = basic_allotment

        logger.debug("Deep Data Allotment: %s", self.__available_deep_data_allotment)
