"""!@package pytrader.libs.utilities.config.abstractbrokerconfig

Abstract Base Class for Broker Configuration

@author G S Derber
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

@file pytrader/libs/utilities/config/broker/abstractbrokerconfig.py
"""
from abc import ABC, abstractmethod

from pytrader.libs.system import logging

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base Logger
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class AbstractBrokerConfig(ABC):
    """!
    Abstract Broker Config.

    Ensures all functions exists for the different brokers.
    """

    @abstractmethod
    def identify_clients(self):
        """!
        Identifies available clients.
        """

    @abstractmethod
    def get_client_address(self):
        """!
        Identifies Client Addresses
        """
