"""!
@package pytrader.libs.clients.broker
Creates a basic interface for interacting with a broker

@file pytrader/libs/clients/broker/__init__.py

Creates a basic interface for interacting with a broker

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

"""
# System libraries
import sys
import threading

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
    Acts as a unifying class for various brokers.  Dynamically selects the correct broker at runtime.

    Currently, only supports Interactive Brokers
    """

    def __new__(cls, *args, **kwargs):
        """!
        Broker Client Class initializer.

        @param *args
        @param **kwargs

        @returun subclass - An instance of one of the potential broker clients.
        """
        subclass_map = {"ibkr": ibkrclient.IbkrClient}

        if args[0] in subclass_map:
            broker = args[0]
        else:
            raise Exception("Invalid Broker Selected")
            sys.exit(1)

        logger.debug3("Subclass Map: %s", subclass_map)
        logger.debug2("Broker: %s", broker)
        logger.debug2("Broker Subclass: %s", subclass_map.get(broker))

        subclass = subclass_map.get(broker)
        return subclass(*args, **kwargs)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def brokerclient(broker):
    """!
    Used to initialize the broker connection.

    @param address - The URL / IP address for the broker server
    @param port - The Port used by the broker server
    @param client_id - The Client ID number.

    @return brokerclient - An instance of the broker client.
    """
    logger.debug10("Begin Function")

    brokerclient = BrokerClient(broker)
    logger.debug10("End Function")
    return brokerclient


def run_loop(client):
    logger.debug10("Begin Function")
    api_thread = threading.Thread(target=client.run, daemon=True)

    logger.debug2("Start Broker Client Thread")
    api_thread.start()
    logger.debug2("Broker Client Thread Started")
    logger.debug10("End Function")
    return api_thread
