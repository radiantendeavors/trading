"""!@package pytrader.libs.utilities.config.brokerconfig.tws

Manages the configuration for TWS API clients

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

@file pytrader/libs/applications/broker/__init__.py
"""
from pytrader import git_branch
from pytrader.libs.clients.broker.ibkr.tws.ibgdemo import IbgDemoAccountClient
from pytrader.libs.clients.broker.ibkr.tws.ibgreal import IbgRealAccountClient
from pytrader.libs.clients.broker.ibkr.tws.twsdemo import TwsDemoAccountClient
from pytrader.libs.clients.broker.ibkr.tws.twsreal import TwsRealAccountClient
from pytrader.libs.system import logging
from pytrader.libs.utilities.config.broker.abstractbrokerconfig import \
    AbstractBrokerConfig

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
class TwsConfig(AbstractBrokerConfig):
    """!
    Provides the configuration for TWSAPI clients.
    """

    # This should probably be a singleton class.  I don't see any reason for more than once
    # instance.  And having only one instance could probably simplify a few things.
    available_ports = []

    def __init__(self, address: str = "127.0.0.1") -> None:
        """!
        Initializes the TwsConfig Class.

        @param address: sets the ip address or url of the tws application.

        @return None
        """
        if git_branch == "main":
            self.potential_ports = [7496, 7497, 4001, 4002]
        else:
            self.potential_ports = [7497, 4002]

        self.potential_clients = {
            "twsreal": TwsRealAccountClient,
            "twsdemo": TwsDemoAccountClient,
            "ibgreal": IbgRealAccountClient,
            "ibgdemo": IbgDemoAccountClient
        }
        self.address = address

    def get_client_address(self) -> str:
        """!
        Provides the client url or ip address.

        @return self.address: Client url or ip address
        """
        return self.address

    def identify_clients(self) -> dict:
        """!
        Identifies detected clients.

        @return clients: Dictionary of Client Class Objects
        """
        client_identifiers = {7496: "twsreal", 7497: "twsdemo", 4001: "ibgreal", 4002: "ibgdemo"}
        clients = {}

        self._set_broker_ports()

        for port in self.available_ports:
            client_id = client_identifiers.get(port)
            clients[client_id] = self.potential_clients.get(client_id)

        return clients

    def _check_if_ports_available(self, port: int) -> bool:
        """!
        Checks if a given port is available

        @param port: The port to check

        @return bool: True if the port is available, False if it is not available.
        """
        if git_branch == "main" and port in [7496, 7497, 4001, 4002]:
            return True

        if git_branch != "main" and port in [7497, 4002]:
            return True

        return False

    def _set_broker_ports(self) -> None:
        """!
        Creates a list of available ports to connect to the broker.

        return None
        """
        for port in self.potential_ports:
            if self._check_if_ports_available(int(port)):
                self.available_ports.append(int(port))
        logger.debug9("Available ports: %s", self.available_ports)
