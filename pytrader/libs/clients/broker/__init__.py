"""!
@package pytrader.libs.clients.broker
Creates a basic interface for interacting with a broker

@file pytrader/libs/clients/broker/__init__.py

Creates a basic interface for interacting with a broker

@author Geoff S. derber
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

"""
# System libraries
import threading
import time

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs.clients.broker import ibkrclient

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
class BrokerClient():
    """!
    @brief Acts as a unifying class for various brokers.  Dynamically selects the correct broker at
    runtime.

    Currently, only supports Interactive Brokers
    """

    def __new__(cls, *args, **kwargs):
        """!
        Broker Client Class initializer.

        @param *args
        @param **kwargs
        """
        broker = kwargs["broker"]
        subclass_map = {"ibkr": ibkrclient.IbkrClient}

        logger.debug3("Subclass Map: %s", subclass_map)
        logger.debug2("Broker: %s", broker)
        logger.debug2("Securities Subclass: %s", subclass_map.get(broker))

        subclass = subclass_map.get(broker)
        return subclass(*args, **kwargs)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def broker_connect(address, port, client_id=0):
    """!
    Used to initialize the broker connection.

    @param address
    @param port
    @param client_id

    """
    logger.debug10("Begin Function")
    logger.debug("Address: %s Port: %s", address, port)
    if client_id < 1:
        logger.warning("Self.Client ID: %s", client_id)
    else:
        logger.debug("Client ID: %s", client_id)

    # Connect to TWS or IB Gateway
    brokerclient = BrokerClient(broker="ibkr")
    brokerclient.connect(address, port, client_id)

    logger.debug2("Start Broker Client Thread")
    broker_thread = threading.Thread(target=brokerclient.run)
    broker_thread.start()
    logger.debug2("Broker Client Thread Started")
    next_order_id = brokerclient.get_next_order_id()
    logger.debug("Received next order id: %s", next_order_id)
    time.sleep(1)

    brokerclient.check_server()

    logger.debug10("End Function")
    return brokerclient
