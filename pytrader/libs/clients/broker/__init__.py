"""!
@package pytrader.libs.clients.broker

Provides the broker client

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


@file lib/clients/broker/__init__.py

  Creates a basic interface for interacting with a broker

"""
# System libraries

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
class BrokerClient(ibkrclient.IbkrClient):
    """! @class BrokerClient

    @brief Provides the client interface to the broker"""

    def __init__(self, *args, **kwargs):
        """! Broker Client Class initializer.

        @param address The IP Address for the client.
        @param port The port for the client.
        @param client_id The id number for the client
        """

        super().__init__(*args, **kwargs)
