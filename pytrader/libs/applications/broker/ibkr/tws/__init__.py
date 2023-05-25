"""!@package pytrader.libs.applications.broker.tws

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

@file pytrader/libs/applications/broker/tws.py
"""
# System Libraries
import socket
import threading
from multiprocessing import Queue

# 3rd Party Libraries
from ibapi import contract
from ibapi import order
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.applications.broker import common
#from pytrader.libs.clients.broker.ibkr.tws import TwsApiClient

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
class TwsBaseClient(EWrapper, EClient):
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

        ## Message Queue
        self.queue = None

        ## Track the API Thread
        self.api_thread = threading.Thread(target=self.run, daemon=True)

        ## Used to track if the next valid id is available
        self.next_valid_id_available = threading.Event()

        ##
        self.accounts_available = threading.Event()

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


class Tws(common.BrokerClient):

    def __init__(self):
        ## Broker Address
        self.address = "127.0.0.1"

        ## Broker Client
        self.brokerclient = None

        ## Data Queue
        self.queue = None

        ## Client ID
        self.client_id = 2004

    def set_broker_client(self, brokerclient):
        self.brokerclient = brokerclient

    def set_data_queue(self, data_queue):
        """!
        Set's the data queue and broker client.
        """
        self.queue = data_queue

    def update_client_id(self, client_id: int):
        """!
        Updates the client Id.

        @param client_id: The client's unique id number.

        @return None
        """
        logger.debug(
            "Begin Function 'Update Client Id'.  New client id is: %s",
            client_id)
        self.client_id = client_id
        logger.debug("End Function")
