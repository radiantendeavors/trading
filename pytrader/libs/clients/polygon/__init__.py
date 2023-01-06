"""
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
from polygon import RESTClient

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs.utilities import config

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
class PolygonClient(RESTClient):
    """
    @brief Short term, this class does absolutely nothing.  Long term, I'd like to add the ability
    to interface with multiple brokers.  This class will act as the interface between the different
    brokers.

    """

    def __init__(self, *args, **kwargs):
        """
        Broker Client Class initializer.

        @param *args
        @param **kwargs
        """

        if kwargs.get("api_key"):
            api_key = kwargs["api_key"]

        else:
            conf = config.Config()
            conf.read_config()
            api_key = conf.get_polygon_api_key()

        super().__init__(api_key)
