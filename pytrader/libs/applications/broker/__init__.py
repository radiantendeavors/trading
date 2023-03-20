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
import json
import socket
import os

# 3rd Party Libraries
from ibapi import contract

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients import broker
from pytrader.libs.utilities import ipc

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

"""
logger = logging.getLogger(__name__)

## List of potential ports TWS/IB Gateway could listen on.
ALLOWED_PORTS = [7496, 7497, 4001, 4002]


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class BrokerProcess():

    def __init__(self, address: str = "127.0.0.1"):
        self.address = address
        self.available_ports = []
        self.brokerclient = broker.BrokerClient("ibkr")
        self.contracts = {}
        self.socket_server = ipc.IpcServer()

    def run(self, client_id):
        thread_queue = queue.Queue()

        #self._set_broker_ports()
        #self._start_threads(client_id)

        broker_connection = True
        self.socket_server.start_thread(thread_queue)

        #while broker_connection:

        #broker_connection = self.brokerclient.is_connected()

        return None

    def _check_if_ports_available(self, port):
        logger.debug("Begin Function")
        tws_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.debug("End Function")
        return tws_socket.connect_ex((self.address, port)) == 0

    def _create_contracts(self, tickers):
        for item in tickers:
            contract_ = contract.Contract()
            contract_.symbol = item
            contract_.secType = "STK"
            contract_.exchange = "SMART"
            contract_.currency = "USD"
            self.contracts[item] = contract_

    def _set_broker_ports(self):
        logger.debug10("Begin Function")
        # for port in ALLOWED_PORTS:
        #     if self._check_if_ports_available(int(port)):
        #         self.available_ports.append(int(port))
        self.available_ports.append(int(7497))
        logger.debug("Available ports: %s", self.available_ports)
        logger.debug10("End Function")

    def _start_threads(self, client_id):
        """!

        @param client_id: The id of the client to be used.

        @return None
        """
        logger.debug("Begin Function: %s %s %s", self.address,
                     self.available_ports[0], client_id)

        # FIXME: This only connects to the first fucking client available.
        self.brokerclient.connect(self.address, self.available_ports[0],
                                  client_id)

        logger.debug("BrokerClient connected")

        self.brokerclient.start_thread()

        logger.debug("End Function")

    def _stop(self):
        self.stop_thread()

    def _stop_thread(self):
        logger.debug("Begin Function")
        self.brokerclient.stop_thread()
        logger.debug("End Function")
        return None
