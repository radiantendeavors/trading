"""!
@package pytrader.libs.clients.broker.ibkr.tws.twsaccount

Creates the interface for connecting to a Tws Account.

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

@file pytrader/libs/clients/broker/ibkr/tws/twsaccount.py

Creates the interface for connecting to a Tws Account.
"""
# System Libraries

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients.broker.ibkr.tws.twsaccount import TwsAccountClient

# Conditional Libraries

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
class TwsDemoAccountClient(TwsAccountClient):
    """!
    This class provides functionality for connections with TWS Demo Accounts.
    """

    def __init__(self, data_queue: dict) -> None:
        super().__init__(data_queue)
        self.port = 7497
