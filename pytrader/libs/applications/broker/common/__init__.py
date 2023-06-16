"""!
@package pytrader.libs.applications.broker.common

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


@file pytrader/libs/applications/broker/common/__init__.py
"""
# Standard libraries
import datetime
import queue

from abc import ABCMeta, abstractmethod

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
    Contains bar history for a security
    """
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        ## Broker Client
        self.brokerclient = None

        ## Multiprocessing Data Queue
        self.data_queue = None

        ## Broker Thread Queue
        self.queue = None

        ## Next Order Id
        self.next_order_id = 0

    def run(self):
        broker_connection = True
        while broker_connection:
            response_data = self.queue.get()
            #logger.debug("Response Data: %s", response_data)
            if response_data == "Disconnected":
                broker_connection = False
            else:
                self._parse_data(response_data)

    @abstractmethod
    def create_braket_order(self, order_request):
        pass

    @abstractmethod
    def create_order(self, order_request):
        pass

    @abstractmethod
    def request_bar_history(self):
        pass

    def request_global_cancel(self):
        self.brokerclient.req_global_cancel()

    @abstractmethod
    def request_option_details(self):
        pass

    @abstractmethod
    def request_market_data(self):
        pass

    @abstractmethod
    def request_real_time_bars(self):
        pass

    @abstractmethod
    def send_real_time_bars(self, real_time_bar: dict):
        pass

    @abstractmethod
    def send_market_data_ticks(self, market_data: dict):
        pass

    def send_order_id(self):
        message = {"next_order_id": self.next_order_id}
        self.data_queue.put(message)

    @abstractmethod
    def send_order_status(self, order_status: dict):
        pass

    def set_attributes(self, brokerclient, data_queue, broker_queue):
        self.brokerclient = brokerclient
        self.data_queue = data_queue
        self.queue = broker_queue

    @abstractmethod
    def set_bar_sizes(self, bar_sizes: list):
        """!
        Abstract method to set bar sizes.
        """
        pass

    @abstractmethod
    def set_contracts(self, contracts):
        pass

    def send_bars(self, contract: Contract, bar_type, bar_size, bars):
        message = {bar_type: {contract.localSymbol: {bar_size: bars}}}
        self.data_queue.put(message)

    def send_ticks(self, contract: Contract, tick):
        message = {"market_data": {contract.localSymbol: tick}}
        self.data_queue.put(message)

    # ==============================================================================================
    #
    # Begin Private Functions
    #
    # ==============================================================================================
    def _parse_data(self, response_data):
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
