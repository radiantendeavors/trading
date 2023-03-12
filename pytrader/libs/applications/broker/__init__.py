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
import threading
import socket

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients import broker

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


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class BrokerProcess():

    def __init__(self, address):
        self.address = address
        self.allowed_ports = [7496, 7497, 4001, 4002]
        self.available_ports = []
        self.brokerclient = broker.BrokerClient("ibkr")

    def check_if_ports_available(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return s.connect_ex((self.address, port)) == 0

    def set_broker_ports(self):
        logger.debug("Begin Function")
        for port in self.allowed_ports:
            if self.check_if_ports_available(int(port)):
                self.available_ports.append(int(port))
        logger.debug("Available ports: %s", self.available_ports)
        logger.debug10("End Function")

    def run(self, client_id):
        self.set_broker_ports()
        self.start_threads(client_id)

        return None

    def start_threads(self, client_id):
        """!

        @param client_id: The id of the client to be used.

        @return None
        """
        logger.debug("Begin Function: %s %s %s", self.address,
                     self.available_ports[0], client_id)

        # FIXME: This only connects to the first fucking client available.
        self.brokerclient.connect(self.address, self.available_ports[0],
                                  client_id)
        logger.debug("Connected")
        self.app_thread = threading.Thread(target=self.brokerclient.run(),
                                           daemon=True)

        self.app_thread.start()
        logger.debug("End Function")

    def stop(self):
        self.stop_thread()

    def stop_thread(self):
        logger.debug("Begin Function")
        self.app_thread.join()
        logger.debug("End Function")
        return None
