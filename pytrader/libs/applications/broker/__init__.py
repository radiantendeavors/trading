"""!@package pytrader.libs.applications.broker

The main user interface for the trading program.

@author G. S. Derber
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
from pytrader.libs.applications.broker.ibkr.tws import Tws
from pytrader.libs.clients.broker.ibkr.tws import TwsClient

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


# ==================================================================================================
#
# BrokerProcess
#
# ==================================================================================================
class BrokerProcess():
    """!
    The Process for interacting with the broker.

    """

    def __init__(self,
                 cmd_queue: Queue,
                 data_queue: Queue,
                 broker_id: str = "twsapi"):
        """!
        Creates an instance of the BrokerProcess.
        """
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue
        self.broker_id = broker_id

        ## Available Ports
        self.available_ports = []

        broker_client_class = {"twsapi": TwsClient()}
        broker_class = {"twsapi": Tws()}

        self.brokerclient = broker_client_class.get(broker_id)
        self.broker = broker_class.get(broker_id)

        self.queue = queue.Queue()

        # I don't really like using this setter, but if I want to be able to add other clients
        # later, I am not sure how to do this differently.
        self.broker.set_broker_client(self.brokerclient)
        self.broker.set_data_queue(data_queue)
        logger.debug("Broker Client: %s", self.brokerclient)

    def configure_client(self, address: str = "", client_id: int = 0):
        """!

        @param client_id: The id of the client to be used.

        @return None
        """
        logger.debug("Begin Function 'Configure Client': %s %s", address,
                     client_id)
        self.address = address
        self.client_id = client_id

        logger.debug("End Function")

    def run(self):
        """!
        Run the broker process as long as the broker is connected.
        """

        self._set_broker_ports()
        self._start_threads()

        try:
            if self.broker_id == "twsapi":
                self.brokerclient.start_threads()

            broker_connection = True
            while broker_connection:
                logger.debug("Loop while connected")
                cmd = self.cmd_queue.get()
                logger.debug("Command: %s", cmd)
                logger.debug("Command Data Type: %s", type(cmd))

                self._process_commands(cmd)
                broker_connection = self.brokerclient.is_connected()

        except KeyboardInterrupt as msg:
            logger.debug("Broker Client Killed by Keyboard Interupt: %s", msg)

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    # def _place_order(self, order_request):
    #     logger.debug("Order Received: %s", order_request)

    #     bracket_check = (order_request.get("profit_target")
    #                      and order_request.get("stop_loss"))

    #     logger.debug("Bracket Check: %s", bracket_check)
    #     if bracket_check:
    #         self._create_braket_order(order_request)
    #     else:
    #         self._create_order(order_request)

    def _process_commands(self, cmd):
        logger.debug("Processing Command: %s", cmd)
        if cmd.get("set"):
            self._set_cmd(cmd["set"])

        # if cmd.get("req"):
        #     self._req_cmd(cmd["req"])

        # if cmd.get("place_order"):
        #     self._place_order(cmd["place_order"])

    # def _req_cmd(self, subcommand):
    #     if subcommand == "bar_history":
    #         self._request_bar_history()
    #     elif subcommand == "option_details":
    #         self._request_option_details()
    #     elif subcommand == "real_time_market_data":
    #         self._request_market_data()
    #     elif subcommand == "real_time_bars":
    #         self._request_real_time_bars()
    #     elif subcommand == "tick_by_tick_data":
    #         self._request_tick_by_tick_data()
    #     elif subcommand == "global_cancel":
    #         self._request_global_cancel()
    #     else:
    #         logger.error("Command Not Implemented: %s", subcommand)

    def _set_broker_ports(self):
        """!
        Creates a list of available ports to connect to the broker.
        """
        for port in ALLOWED_PORTS:
            if self._check_if_ports_available(int(port)):
                self.available_ports.append(int(port))
        logger.debug("Available ports: %s", self.available_ports)

    def _set_cmd(self, subcommand):
        """!
        Processes any subcommand from the 'set' command received from the strategy process.
        """
        logger.debug("Begin Function")
        if subcommand.get("tickers"):
            self.brokerclient.set_contracts(subcommand["tickers"])
            self.data_queue.put("Contracts Created")
        if subcommand.get("bar_sizes"):
            self.brokerclient.set_bar_sizes(subcommand["bar_sizes"])
            self.data_queue.put("Bar Sizes Set")
        logger.debug("End Function")

    def _start_threads(self):
        """!
        @param client_id: The id of the client to be used.
        @return None
        """
        logger.debug(
            "Begin Function 'Start Threads' (Address: %s, Port: %s, Client ID: %s)",
            self.address, self.available_ports[0], self.client_id)

        # TODO: Configure to connect to multiple available clients
        try:
            self.brokerclient.connect(self.address, self.available_ports[0],
                                      self.client_id)
            self.brokerclient.run()
            logger.debug("Broker Connected")

            #next_order_id = self.brokerclient.get_next_order_id()
            next_order_id = 1
            logger.debug("BrokerClient connected, next order id is: %s",
                         next_order_id)

            self.brokerclient.start_thread(self.queue)

        except KeyboardInterrupt as msg:
            logger.debug("KeyboardInterrupt")

        finally:
            self.brokerclient.disconnect()

        logger.debug("End Function")

    def _check_if_ports_available(self, port: int):
        """!
        Checks if a given port is available

        @param port: The port to check

        @return bool: True if the port is available, False if it is not available.
        """
        tws_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return tws_socket.connect_ex((self.address, port)) == 0
