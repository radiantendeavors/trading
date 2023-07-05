"""!@package pytrader.libs.applications.broker

The main user interface for the trading program.

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

@file pytrader/libs/applications/broker/__init__.py
"""
# System Libraries
import queue
import socket
import threading

from multiprocessing import Queue

# 3rd Party Libraries
from ibapi import contract
from ibapi import order

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader import CLIENT_ID
from pytrader.libs.applications.broker.ibkr.tws import TwsDataThread
from pytrader.libs.clients.broker.ibkr.tws import TwsApiClient

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base Logger
logger = logging.getLogger(__name__)

## List of potential ports TWS/IB Gateway could listen on.
ALLOWED_PORTS = [7496, 7497, 4001, 4002]


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class BrokerProcess():
    """!
    The Process for interacting with the broker.

    """

    def __init__(self,
                 cmd_queue: Queue,
                 data_queue: Queue,
                 address: str = "127.0.0.1",
                 broker_id: str = "twsapi",
                 client_id: int = CLIENT_ID):
        """!
        Creates an instance of the BrokerProcess.
        """
        self.address = address
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue
        self.available_ports = []
        self.contracts = {}
        self.client_id = client_id
        broker_client_class = {"twsapi": TwsApiClient()}
        broker_class = {"twsapi": TwsDataThread()}
        self.brokerclient = broker_client_class.get(broker_id)
        self.data_response = broker_class.get(broker_id)
        self.broker_queue = queue.Queue()

        self.data_response.set_attributes(self.brokerclient, self.data_queue, self.broker_queue)
        self.data_thread = threading.Thread(target=self.data_response.run, daemon=True)

    def run(self):
        """!
        Run the broker process as long as the broker is connected.

        @param client_id: The ID number to use for the broker connection.
        """
        self._set_broker_ports()
        self._start_threads()

        broker_connection = True
        while broker_connection:
            cmd = self.cmd_queue.get()
            logger.debug4("Command: %s", cmd)

            self._process_commands(cmd)
            broker_connection = self.brokerclient.is_connected()

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _cancel_order(self, order_id: int):
        """!
        Send Cancel Order to data_response thread.
        """
        self.data_response.cancel_order(order_id)

    def _check_if_ports_available(self, port):
        """!
        Checks if a given port is available

        @param port: The port to check

        @return bool: True if the port is available, False if it is not available.
        """
        tws_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return tws_socket.connect_ex((self.address, port)) == 0

    def _place_order(self, order_request):
        """!
        Send place order to data_response thread.
        """
        logger.debug9("Order Received: %s", order_request)
        self.data_response.create_order(order_request)

    def _process_commands(self, cmd):
        logger.debug4("Processing Command: %s", cmd)
        if cmd.get("set"):
            self._set_cmd(cmd["set"])

        if cmd.get("req"):
            self._req_cmd(cmd["req"])

        if cmd.get("place_order"):
            self._place_order(cmd["place_order"])

        if cmd.get("cancel_order"):
            self._cancel_order(cmd["cancel_order"])

    def _req_cmd(self, subcommand):
        logger.debug4("Request Command: %s", subcommand)
        if subcommand == "bar_history":
            self.data_response.request_bar_history()
        elif subcommand == "option_details":
            self.data_response.request_option_details()
        elif subcommand == "real_time_bars":
            self.data_response.request_real_time_bars()
        elif subcommand == "real_time_market_data":
            self.data_response.request_market_data()
        # elif subcommand == "tick_by_tick_data":
        #     self._request_tick_by_tick_data()
        elif subcommand == "global_cancel":
            self.data_response.request_global_cancel()
        else:
            logger.error("Command Not Implemented: %s", subcommand)

    # def _request_tick_by_tick_data(self):
    #     for key in self.contracts.keys():
    #         self.ticks[key] = ticks.BrokerTicks(contract=self.contracts[key],
    #                                             brokerclient=self.brokerclient,
    #                                             data_queue=self.data_queue)
    #         self.ticks[key].request_ticks()
    #         self.tick_thread[key] = threading.Thread(
    #             target=self.ticks[key].run, daemon=True)
    #         self.tick_thread[key].start()

    def _set_broker_ports(self):
        """!
        Creates a list of available ports to connect to the broker.
        """
        # for port in ALLOWED_PORTS:
        #     if self._check_if_ports_available(int(port)):
        #         self.available_ports.append(int(port))
        self.available_ports.append(int(7497))
        logger.debug9("Available ports: %s", self.available_ports)

    def _set_cmd(self, subcommand):
        """!
        Processes any subcommand from the 'set' command received from the strategy process.
        """
        logger.debug4("Subcommand received: %s", subcommand)
        if subcommand.get("tickers"):
            self.data_response.set_contracts(subcommand["tickers"])
            self.data_queue.put("Contracts Created")
        if subcommand.get("bar_sizes"):
            self.data_response.set_bar_sizes(subcommand["bar_sizes"])
            self.data_queue.put("Bar Sizes Set")

    def _start_threads(self):
        """!

        @param client_id: The id of the client to be used.

        @return None
        """
        # TODO: Configure to connect to multiple available clients
        logger.debug("Client Id: %s", self.client_id)
        self.brokerclient.connect(self.address, self.available_ports[0], self.client_id)
        logger.debug9("BrokerClient connected")

        self.brokerclient.start_thread(self.broker_queue)
        self.data_thread.start()

    def _stop(self):
        """!
        Alias for _stop_thread
        """
        self._stop_thread()

    def _stop_thread(self):
        """!
        Stops the brokerclient thread.
        """
        self.brokerclient.stop_thread()
