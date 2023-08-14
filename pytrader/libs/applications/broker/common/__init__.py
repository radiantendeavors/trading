"""!
@package pytrader.libs.applications.broker.common

Provides a baseline BrokerDataThread common to all brokers.

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


@file pytrader/libs/applications/broker/common/__init__.py
"""
# Standard libraries
import datetime
import queue

from abc import ABCMeta, abstractmethod
from queue import Queue

# 3rd Party libraries
from ibapi.contract import Contract

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs import bars

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
class BrokerDataThread():
    """!
    Provides the Broker Data Response thread.
    """
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        """!
        Initializes the Broker Data Thread.
        """
        ## Broker Client
        self.brokerclient = None

        ## Multiprocessing Data Queue
        self.data_queue = None

        ## Broker Thread Queue
        self.queue = None

        ## Next Order Id
        self.next_order_id = 0

    def run(self):
        """!
        Provides the run loop for the data thread.

        @return None
        """
        broker_connection = True
        while broker_connection:
            response_data = self.queue.get()
            #logger.debug("Response Data: %s", response_data)
            if response_data == "Disconnected":
                broker_connection = False
            else:
                self._parse_data(response_data)

    @abstractmethod
    def create_order(self, order_request):
        """!
        Creates an order from an order request.
        """
        pass

    @abstractmethod
    def request_bar_history(self):
        """!
        Abstract method to request bar history.
        """
        pass

    def request_global_cancel(self):
        """!
        Request to cancel all open orders.
        """
        self.brokerclient.req_global_cancel()

    @abstractmethod
    def request_option_details(self, strategy_id: str):
        """!
        Abstract method to request for option details.
        """
        pass

    @abstractmethod
    def request_market_data(self, strategy_id: str):
        """!
        Abstract method to request streaming market data.
        """
        pass

    @abstractmethod
    def request_real_time_bars(self, strategy_id: str):
        """!
        Abstract method to request real time bars.
        """
        pass

    @abstractmethod
    def send_market_data_ticks(self, market_data: dict):
        """!
        Abstract method to send streaming market data to the strategies.

        @param market_data: The market data to send.
        """
        pass

    def send_order_id(self):
        """!
        Sends the next order id to the strategy.
        """
        message = {"next_order_id": self.next_order_id}
        self.data_queue["Main"].put(message)

    @abstractmethod
    def send_order_status(self, order_status: dict):
        """!
        Sends the current order status to the strategy.

        @param order_status: The current order status.
        """
        pass

    @abstractmethod
    def send_real_time_bars(self, real_time_bar: dict):
        """!
        Abstract method to send real time bars to the strategies.

        @param real_time_bar: The real time bar to send to the strategies.

        @return None
        """
        pass

    def set_attributes(self, brokerclient, data_queue: dict, broker_queue: Queue) -> None:
        """!
        Sets class attributes.
        """
        self.brokerclient = brokerclient
        self.data_queue = data_queue
        self.queue = broker_queue

    @abstractmethod
    def set_bar_sizes(self, bar_sizes: list, strategy_id: str):
        """!
        Abstract method to set bar sizes.
        """
        pass

    @abstractmethod
    def set_contracts(self, contracts: dict, strategy_id: str):
        """!
        Abstract method to set the contracts.
        """
        pass

    # def send_ticks(self, contract: Contract, tick):
    #     """!
    #     Sends tick data to the strategies.

    #     @param contract: The contract for the bar to send.
    #     @param tick: The tick data to send.

    #     @return None
    #     """
    #     ticker = contract.localSymbol
    #     message = {"market_data": {contract.localSymbol: tick}}
    #     for strategy_id in self.contract_strategies[ticker]:
    #         self.data_queue[strategy_id].put(message)

    # ==============================================================================================
    #
    # Begin Private Functions
    #
    # ==============================================================================================
    def _parse_data(self, response_data: dict):
        """!
        Parses data from the broker client.

        @param response_data: The data response from the broker client.

        @return None
        """
        if response_data.get("real_time_bars"):
            self.send_real_time_bars(response_data["real_time_bars"])
        elif response_data.get("market_data"):
            self.send_market_data_ticks(response_data["market_data"])
        elif response_data.get("next_order_id"):
            # We really only want to update the order id the first time we receive it.  Afterwards,
            # we use our own tracking to ensure we do not make multiple orders with the same id.
            if self.next_order_id == 0:
                self.next_order_id = response_data["next_order_id"]
                self.send_order_id()
        elif response_data.get("order_status"):
            self.send_order_status(response_data)
