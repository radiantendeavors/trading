"""!
@package pytrader.libs.clients.broker.twsapibase

Provides the client for Interactive Brokers

@author Geoff S. Derber
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

  Creates a basic interface for interacting with Interactive Brokers.

@file pytrader/libs/clients/broker/twsapibase.py

Provides the client for Interactive Brokers
"""
# Standard Libraries
import threading
from queue import Queue

# 3rd Party Libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

# Standard Library Overrides
from pytrader.libs.system import logging

# Other Libraries
from pytrader.libs.clients.broker import BrokerClient

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## Instance of Logging class
logger = logging.getLogger(__name__)

## List of potential ports TWS/IB Gateway could listen on.
ALLOWED_PORTS = [7496, 7497, 4001, 4002]


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class TwsBaseClient(EWrapper, EClient, BrokerClient):
    """!
    Serves as the client interface for Interactive Brokers
    """

    def __init__(self, *args, **kwargs):
        """!
        Initialize the IbkrClient class

        @param *args
        @param **kwargs

        @return An instance of the IbkrClient class.
        """
        EWrapper.__init__(self)
        EClient.__init__(self, self)

        ##
        self.available_ports = []

        ## Message Queue
        self.queue = None

        ## Track the API Thread
        self.api_thread = threading.Thread(target=self.run, daemon=True)

    def start_thread(self, queue: Queue):
        """!
        Starts the API thread.
        """
        self.queue = queue
        self.api_thread.start()

    def stop_thread(self):
        """!
        Stops the API thread.
        """
        self.api_thread.join()

    def is_connected(self):
        """!
        Identifies if client is connected to TWS.
        """
        return True
