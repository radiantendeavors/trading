"""!@package pytrader.libs.applications.broker

The main user interface for the trading program.

@author Geoff S. Derber
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

@file pytrader/libs/applications/broker/__init__.py
"""
# System Libraries
import queue
import socket
import threading

from abc import ABCMeta, abstractmethod
from multiprocessing import Queue

# 3rd Party Libraries
from ibapi import contract
from ibapi import order

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries

# Conditional Libraries

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
class BrokerClient():
    """!
    Creates a client instance of the broker.
    """

    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        """!
        Initializes the BrokeClient Class

        @param args:
        @param kwargs:

        @return None
        """
        ## Thread Message Queue
        self.queue = queue.Queue()

        ## Process Data Queue
        self.data_queue = args[0]

        ## Ticker List
        self.ticker_list = []

        ## Bar Sizes
        self.bar_sizes = []

    def change_address(self, address: str):
        """!
        Changes the address used by TWS Client."""
        logger.debug("Begin Function 'Change Address'")
        self.address = address
        logger.debug("End Function")

    @abstractmethod
    def is_connected(self):
        """!
        Abstract method to check if the client is connected to the broker.
        """
        logger.error("Connection Check: Not implemented")

    @abstractmethod
    def request_ticks(self, *args):
        """!
        Abstract method to request tick information from the broker.
        """
        logger.error("Request Ticks: Not implemented")

    def run(self):
        """!
        Runs the client as long as the client is connected.
        """
        broker_connection = True
        while broker_connection:
            data = self.queue.get()
            self._process_data(data)
            broker_connection = self.is_connected()

    @abstractmethod
    def start_threads(self):
        """!
        Starts threads
        """
        logger.error("Starting Threads: Not implemented")

    def stop(self):
        """!
        Alias for _stop_thread
        """
        self.stop_thread()

    @abstractmethod
    def stop_thread(self):
        """!
        Abstract method to stop the thread.
        """
        logger.error("Not implemented")

    # ==============================================================================================
    #
    # Internal Use only functions.  These should not be used outside the class.
    #
    # ==============================================================================================
    def _process_data(self, data):
        """!
        Processes data received from the broker.
        """
        func_map = {
            "contract_details": self._add_contract,
            "head_time_stamp": self._send_head_time_stamp,
            "real_time_bar": self._send_real_time_bar,
            "tick_by_tick_all_last": self._send_tick_by_tick_data,
            "tick_generic": self._send_mkt_data,
            "tick_option_computation": self._send_mkt_data,
            "tick_price": self._send_mkt_data
        }

        key = data.keys()[0]
        func = func_map.get(key)
        func(data[key])

    @abstractmethod
    def _add_contract(self, data):
        """!
        Abstract method to add contracts.
        """
        logger.error("Adding Contract")

    @abstractmethod
    def _send_bars(self, data):
        """!
        Abstract method to send bar data to the strategies.
        """
        logger.debug("Send Bar Data")

    def _send_head_time_stamp(self, data):
        logger.debug("Sending Head Timestamp: %s", data)

    @abstractmethod
    def _send_mkt_data(self, data):
        logger.debug("Sending Ticks: %s", data)

    @abstractmethod
    def _send_real_time_bar(self, data):
        logger.debug("Sending Ticks: %s", data)

    def _send_tick_by_tick_data(self, data):
        logger.debug("Sending Tick-By-Tick Data: %s", data)

    @abstractmethod
    def _send_ticks(self, data):
        logger.debug("Sending Ticks: %s", data)
